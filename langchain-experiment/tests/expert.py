from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import (
    PydanticOutputParser,
    OutputFixingParser,
    RetryWithErrorOutputParser,
)
from langchain_core.exceptions import OutputParserException

import json

from pydantic_core import ValidationError

class TextTestResult(BaseModel):
    is_true: bool = Field(..., description="Whether the claim is true based on the text")
    why: str = Field(..., description="A brief explanation of why the statement is true or false")

def check_text_entail_claim(text: str, claim: str) -> TextTestResult:
    schema_json = json.dumps(TextTestResult.model_json_schema(), indent=2)

    prompt = ChatPromptTemplate.from_template(
"""
You are an expert evaluating claims against the text.
Claims can be about what is explicitly stated in the text. For example:

Text: "The sky is blue."
Claim: "Blue is the sky's color."
Result: true, because the statement is a paraphrase of the text.

Claims can be about the qualities of the text. For example:

Text: "The sky is blue."
Claim: "Mentions sky"
Result: true, because the text mentions the sky.

Text: "The sky is blue."
Claim: "Mentions bicycles"
Result: false, because the text does not mention bicycles.

Text: "The sky is blue."
Claim: "Does not mention bicycles"
Result: true, because the text does not mention bicycles.

Allow for broad, vague, inaccurate claims as long as they don't contradict the text.

When you explain why a claim is true or false, be as specific as possible, citing 
specific parts of the text that support your conclusion.

Output ONLY valid JSON that matches this JSON Schema:
{schema}

Now evaluate:

Text:
{text}

Claim:
{claim}

JSON only; no extra keys, no prose, no code fences.

{format_instructions}
""")

    model = init_chat_model("ollama:llama3.2:3b", temperature=0)
    base_parser = PydanticOutputParser(pydantic_object=TextTestResult)
    fixing_parser = OutputFixingParser.from_llm(parser=base_parser, llm=model)
    retry_parser = RetryWithErrorOutputParser.from_llm(parser=fixing_parser, llm=model)

    last_err = None
    for _ in range(3):
        try:
            prompt_value = prompt.format_prompt(
                schema=schema_json,
                format_instructions=base_parser.get_format_instructions(),
                text=text,
                claim=claim,
            )
            raw = model.invoke(prompt_value)

            return retry_parser.parse_with_prompt(raw.content, prompt_value)
        except (OutputParserException, ValidationError, ValueError) as e:
            last_err = e
            print(f"retry! {raw.content if 'raw' in locals() else '<no response yet>'} because {e}")
            continue

    return TextTestResult(
        is_true=False,
        why=f"Failed to parse LLM output after retries: {last_err}"
    )

def assert_text_entails_claim(text: str, claim: str) -> None:
    result = check_text_entail_claim(text, claim)
    if not result.is_true:
        raise AssertionError(f"Claim is false: {result.why}")
