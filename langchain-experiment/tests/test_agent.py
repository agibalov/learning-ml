from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from expert import assert_text_entails_claim

call_log = []

@tool(parse_docstring=True)
def get_weather(location: str) -> str:
    """Get the current weather in a given location.
    
    Args:
        location: The location to get the weather for.
    """
    global call_log
    call_log.append(("get_weather", location))
    return f"{location}: 72 F, clear"

@tool(parse_docstring=True)
def get_local_time(location: str) -> str:
    """Get the current local time in a given location.
    
    Args:
        location: The location to get the time for.
    """
    global call_log
    call_log.append(("get_local_time", location))
    return "12:34:56"

def test_agent_works_one_step():
    memory = MemorySaver()
    model = init_chat_model("ollama:llama3.2:3b")
    tools = [get_weather, get_local_time]
    agent = create_react_agent(model.bind_tools(tools), tools, checkpointer=memory)

    global call_log
    call_log = []

    out = agent.invoke(
        {"messages": [HumanMessage("What is the weather in New Jersey? Also, what's the local time there.")]},
        config={"configurable": {"thread_id": "andrey-1"}}
    )
    response = out["messages"][-1].content
    print(response)
    assert_text_entails_claim(response, "The weather in New Jersey is 72 F and clear.")
    assert_text_entails_claim(response, "Local time in New Jersey is 12:34:56.")    
    assert len(call_log) == 2
    assert ("get_weather", "New Jersey") in call_log
    assert ("get_local_time", "New Jersey") in call_log

def test_agent_works_two_steps():
    memory = MemorySaver()
    model = init_chat_model("ollama:llama3.2:3b")
    tools = [get_weather, get_local_time]
    agent = create_react_agent(
        model.bind_tools(tools), 
        tools, 
        checkpointer=memory, 
        prompt="""
You are a tool-using assistant in a multi-turn chat with memory.
When you provide answer, use the context from the previous conversation, but
do not repeat the answer to previous question.
""")

    global call_log
    
    call_log = []
    out = agent.invoke(
        {"messages": [HumanMessage("What is the weather in New Jersey?")]},
        config={"configurable": {"thread_id": "andrey-1"}}
    )
    response = out["messages"][-1].content
    print(response)
    assert_text_entails_claim(response, "The weather in New Jersey is 72 F and clear.")
    assert_text_entails_claim(response, "Doesn't say what current time is there.")
    assert len(call_log) == 1
    assert ("get_weather", "New Jersey") in call_log

    call_log = []
    out = agent.invoke(
        {"messages": [HumanMessage("And what time is it there?")]},
        config={"configurable": {"thread_id": "andrey-1"}}
    )
    response = out["messages"][-1].content
    print(response)
    assert_text_entails_claim(response, "Time in New Jersey is 12:34.")
    assert_text_entails_claim(response, "Says nothing about the weather.")
    assert len(call_log) == 1
    assert ("get_local_time", "New Jersey") in call_log
