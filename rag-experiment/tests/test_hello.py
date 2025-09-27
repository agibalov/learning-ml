from contextlib import closing
import sqlite3
import sqlite_vec
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from pathlib import Path
from typing import List
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic_ai import ModelSettings
from pydantic_ai.agent import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic import BaseModel
from dataclasses import dataclass
import json


@dataclass
class SourceDocument:
    filename: str
    content: str


@dataclass
class DocumentChunk:
    source_file: str
    chunk_index: int
    total_chunks: int
    content: str
    char_count: int
    token_count: int


def is_relevant(question: str, text: str) -> tuple[bool, str]:
    class Answer(BaseModel):
        relevant: bool
        reason: str
    model = OpenAIChatModel(
        model_name='gpt-oss:20b',
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
        settings=ModelSettings(temperature=0.0)
    )
    agent = Agent(
        model=model,
        output_type=Answer,
        system_prompt="""
        Given a question and a text, determine if text is relevant to a question or not.
        """.strip()
    )
    response = agent.run_sync(json.dumps({
        "question": question,
        "text": text
    }))
    return (response.output.relevant, response.output.reason)

def answer_question(query: str, context: List[str]) -> tuple[str, bool]:
    class Answer(BaseModel):
        answer: str
        found_answer: bool
    model = OpenAIChatModel(
        model_name='gpt-oss:20b',
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
        settings=ModelSettings(temperature=0.0)
    )
    agent = Agent(
        model=model,
        output_type=Answer,
        system_prompt="""
        Give a question and a context, provide a concise and accurate answer based on the context.

        Prefer answers explicitly stated in the context.
        If there are none, you should infer and draw conclusions, but only from what is in the context.
        If not enough info, say: "The context does not provide the answer."
        """.strip()
    )
    response = agent.run_sync(json.dumps({
        "question": query,
        "context": context
    }))
    return (response.output.answer, response.output.found_answer)


def test_llm():
    assert is_relevant(
        "What is the capital of France?",
        "Paris is the capital and most populous city of France.")[0] is True
    assert is_relevant(
        "How do I make chicken noodle soup?",
        "Paris is the capital and most populous city of France.")[0] is False


def load_docs(docs_dir: str) -> List[SourceDocument]:
    docs_path = Path(docs_dir)
    markdown_files = []
    for file_path in docs_path.glob("*.md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            source_doc = SourceDocument(
                filename=file_path.name,
                content=content
            )
            markdown_files.append(source_doc)
            print(f"Loaded: {file_path.name} ({len(content)} characters)")

    return markdown_files


def chunk_text(text: str, max_tokens: int, overlap_tokens: int) -> List[str]:
    encoding = tiktoken.get_encoding("cl100k_base")

    def tiktoken_len(text: str) -> int:
        return len(encoding.encode(text))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=overlap_tokens,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_text(text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def chunk_docs(docs: List[SourceDocument],
               max_tokens: int,
               overlap_tokens: int) -> List[DocumentChunk]:

    doc_chunks = []
    encoding = tiktoken.get_encoding("cl100k_base")

    for doc in docs:
        normalized_content = '\n'.join(line.strip() for line in doc.content.split('\n') if line.strip())
        if not normalized_content:
            continue

        chunks = chunk_text(normalized_content, max_tokens, overlap_tokens)
        for i, chunk in enumerate(chunks):
            token_count = len(encoding.encode(chunk))

            doc_chunk = DocumentChunk(
                source_file=doc.filename,
                chunk_index=i,
                total_chunks=len(chunks),
                content=chunk,
                char_count=len(chunk),
                token_count=token_count
            )
            doc_chunks.append(doc_chunk)

    return doc_chunks

def create_schema(conn: sqlite3.Connection):
    with closing(conn.cursor()) as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
            doc_id INTEGER,
            embedding FLOAT[384]
        )
        """)
        conn.commit()

def ingest_docs(conn: sqlite3.Connection,
                docs: List[SourceDocument],
                max_tokens: int,
                overlap_tokens: int,
                encoder: SentenceTransformer):

    chunks = chunk_docs(docs, max_tokens, overlap_tokens)
    chunk_contents = [chunk.content for chunk in chunks]
    embeddings = encoder.encode(chunk_contents)

    with closing(conn.cursor()) as cur:
        for id, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                "INSERT INTO chunks (id, content) VALUES (?, ?)",
                (id, chunk.content)
            )

            blob = np.asarray(emb, dtype=np.float32).tobytes()
            cur.execute(
                "INSERT INTO embeddings (doc_id, embedding) VALUES (?, ?)",
                (id, sqlite3.Binary(blob))
            )
        conn.commit()

class QueryContextProvider:
    def __init__(self, conn: sqlite3.Connection, encoder: SentenceTransformer):
        self.conn = conn
        self.encoder = encoder

    def get_context(self, query_text: str) -> List[str]:
        query_embedding = self.encoder.encode([query_text])[0]
        query_embedding_blob = np.asarray(query_embedding, dtype=np.float32).tobytes()
        with closing(self.conn.cursor()) as cur:
            cur.execute("""
                SELECT
                    d.id,
                    d.content,
                    e.distance
                FROM embeddings e
                JOIN chunks d ON e.doc_id = d.id
                WHERE e.embedding MATCH ? AND k = 10
                ORDER BY e.distance
            """, (sqlite3.Binary(query_embedding_blob),))

            vector_results = cur.fetchall()

        reranked_results = []
        cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
        query_doc_pairs = [(query_text, content) for _, content, _ in vector_results]
        cross_scores = cross_encoder.predict(query_doc_pairs)
        for (doc_id, content, distance), cross_score in zip(vector_results, cross_scores):
            result = {
                'doc_id': doc_id,
                'content': content,
                'distance': distance,
                'cross_score': cross_score
            }
            reranked_results.append(result)

        reranked_results.sort(key=lambda result: result['cross_score'], reverse=True)
        reranked_results = reranked_results[:3]

        print("*" * 80)
        print(f"Query: '{query_text}'")
        print("Results:")
        context = []
        for result in reranked_results:
            is_relevant_flag, reason = is_relevant(query_text, result['content'])
            print(f"  ID: {result['doc_id']}, Content: '{result['content'][:100]}...'".replace("\n", " "))
            print(f"  Distance: {result['distance']:.4f}, Cross-Encoder Score: {result['cross_score']:.4f}, " +
                  f"Relevant: {is_relevant_flag}, Reason: {reason}")
            print()

            if is_relevant_flag:
                context.append(result['content'])

        return context


def respond(query_text: str,
            query_context_provider: QueryContextProvider) -> tuple[str, bool]:

    query_context = query_context_provider.get_context(query_text)
    answer, found_answer = answer_question(query=query_text, context=query_context)
    return answer, found_answer


def test_hello():
    conn = sqlite3.connect(":memory:")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)

    create_schema(conn)

    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    docs = load_docs("docs")
    ingest_docs(conn, docs, max_tokens=500, overlap_tokens=100, encoder=encoder)

    query_context_provider = QueryContextProvider(conn, encoder)

    for query_text in ["i need to cook some food. what should I do?",
                       "how do I become a better programmer?",
                       "what are some general-purpose programming languages?",
                       "compare python and java"]:

        answer, found_answer = respond(query_text, query_context_provider)
        print(f"Found Answer: {found_answer}")
        print(f"Answer: {answer}")
        print("\n\n")
