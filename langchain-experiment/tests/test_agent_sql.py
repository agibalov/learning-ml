from typing import Type
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import ToolException, BaseTool
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field
import sqlite3
import pytest

from tabulate import tabulate

from expert import assert_text_entails_claim
from debug_utils import pretty_agent_output

class RunSqlArgs(BaseModel):
    query: str = Field(..., description="Full SQL with concrete values; no '?' placeholders.")


class DatabaseTool(BaseTool):
    name: str = "db_tool"
    description: str = "Tool for querying a SQL database."
    args_schema: Type[BaseModel] = RunSqlArgs
    handle_tool_error = lambda self, e: f"{e}"
    conn: sqlite3.Connection

    def _run(self, query: str) -> str:
        print(f"Running SQL: {query}")

        try:
            self.conn.execute("EXPLAIN " + query)            
        except sqlite3.Error as e:
            print(f"Invalid SQL: {e}")
            raise ToolException(f"INPUT_ERROR: Invalid SQL - {e}")

        try:
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            return tabulate(rows, headers=cols, tablefmt="github")
        except Exception as e:
            print(f"Error running SQL: {e}")
            raise ToolException(f"INPUT_ERROR: Error running SQL - {e}")


SCHEMA = """
        CREATE TABLE persons (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        );
""" 

def make_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO persons(id, name, age) VALUES (?,?,?)",
                    [(1, "Alice", 25),
                    (2, "Bob", 35),
                    (3, "Charlie", 45)])
    return conn    

@pytest.fixture(params=["ollama:llama3.2:3b", "ollama:gpt-oss:20b"],
                ids=lambda v: "model_" + v.replace(":", "_").replace(".", "_").replace("-", "_"))
def model_name(request) -> str:
    return request.param

@pytest.fixture(params=[0.0, 0.2, 0.6, 1.0], 
                ids=lambda v: f"temp_{v:g}".replace(".", "_"))
def temp(request) -> float:
    return request.param

@pytest.fixture(params=[0, 1337, 2302, 31337], 
                ids=lambda v: f"seed_{v}")
def seed(request) -> int:
    return request.param

@pytest.fixture
def agent(model_name: str, temp: float, seed: int) -> CompiledStateGraph:
    conn = make_db()       
    database_tool = DatabaseTool(conn=conn)
    
    memory = MemorySaver()
    model = init_chat_model(model_name, temperature=temp, seed=seed, num_ctx=4096)
    tools = [database_tool]
    agent = create_react_agent(
        model.bind_tools(tools), 
        tools, 
        checkpointer=memory, 
        prompt=AGENT_PROMPT)
    return agent

def test_count_persons_older_than_30(agent: CompiledStateGraph):
    out = agent.invoke(
        {"messages": [HumanMessage("How many persons are older than 30?")]},
        config={"configurable": {"thread_id": f"andrey-1"}}, 
        recursion_limit=10
    )
    response = out["messages"][-1].content
    print(f"Response: {response}")
    assert_text_entails_claim(response, "text contains number 2 or word 'two'")
    pretty_agent_output(out)

def test_average_age(agent: CompiledStateGraph):
    out = agent.invoke(
        {"messages": [HumanMessage("What's the average age of a person?")]},
        config={"configurable": {"thread_id": f"andrey-1"}}, 
        recursion_limit=10
    )
    response = out["messages"][-1].content
    print(f"Response: {response}")
    assert_text_entails_claim(response, "text contains number 35 or word 'thirty five'")

def test_name_of_oldest_person(agent: CompiledStateGraph):
    out = agent.invoke(
        {"messages": [HumanMessage("What's the name of the oldest person?")]},
        config={"configurable": {"thread_id": f"andrey-1"}}, 
        recursion_limit=10
    )
    response = out["messages"][-1].content
    print(f"Response: {response}")
    assert_text_entails_claim(response, "text contains 'Charlie'")


AGENT_PROMPT = f"""
You are an agent that answers questions by querying an SQL database via a tool named `db_tool`.

FOLLOW THESE RULES EXACTLY

1) READ THE SCHEMA FIRST. Use only tables/columns that exist.
2) READ-ONLY: Use SELECT only. Never modify data.
3) EXPLICIT COLUMNS: Never use `*` in SELECT lists.
   EXCEPTION: `COUNT(*)` is allowed in aggregate count queries.
4) INLINE VALUES: No placeholders like `?`. Write concrete values in SQL.
5) WHEN TO USE THE TOOL: If the answer requires DB data, you MUST call the tool.
6) TOOL CALL FORMAT (ReAct):
   Action: db_tool
   Action Input: {{"query": "<SQL string>"}}
   (No extra text on those two lines.)

COUNT QUESTIONS (CRITICAL)

7) If the user asks “how many…”, “count…”, “number of…”, or any equivalent:
   a) Use an aggregate count query:
      SELECT COUNT(*) AS count FROM <table> WHERE <conditions>;
   b) Do NOT select any other columns.
   c) FINAL ANSWER must be ONLY the count number or a minimal sentence with that number.
      Allowed: `2`  or  `There are 2.`
      Not allowed: listing names/ages, extra commentary, guesses.

ERRORS & RETRIES

8) If the tool output includes 'INPUT_ERROR':
   - Read the message, fix the SQL, and CALL THE TOOL AGAIN.
   - Each retry must change the SQL (address the error). Do not repeat the same query.

SCOPE & BREVITY

9) Only answer what was asked. No extra info or speculation.
10) If the question does not require DB access, answer directly without using the tool.

SAFETY CHECK BEFORE EACH CALL

11) Ensure:
   - Query starts with SELECT
   - Columns exist in the schema
   - No `*` in SELECT list (except `COUNT(*)`)
   - Concrete values (no `?`)

DATABASE SCHEMA
{SCHEMA}

EXAMPLES (COPY THIS PATTERN)

Example 1 — Count
User: "How many persons older than 30?"
Action: db_tool
Action Input: {{"query": "SELECT COUNT(*) AS count FROM persons WHERE age > 30"}}
(After tool returns e.g. count=2)
Final Answer: 2

Example 2 — Synonyms of “how many”
User: "Number of people with age >= 65?"
Action: db_tool
Action Input: {{"query": "SELECT COUNT(*) AS count FROM persons WHERE age >= 65"}}
(Observation returns count)
Final Answer: There are 5.

Example 3 — Don’t list when the user asked for a count
(WRONG attempt for illustration — do NOT produce this in real attempts)
Action: db_tool
Action Input: {{"query": "SELECT name, age FROM persons WHERE age > 30"}}
(Observation: INPUT_ERROR or not what user asked)
(Corrected NEW query)
Action: db_tool
Action Input: {{"query": "SELECT COUNT(*) AS count FROM persons WHERE age > 30"}}
Final Answer: 2

Example 4 — Non-count question (list)
User: "List names of persons older than 30."
Action: db_tool
Action Input: {{"query": "SELECT name FROM persons WHERE age > 30 ORDER BY name"}}
(After rows)
Final Answer: <only the requested names>
"""
