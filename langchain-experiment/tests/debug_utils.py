import json
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage


def msg_compact(m: BaseMessage):
    d = {"type": m.type, "content": m.content}
    if isinstance(m, AIMessage):
        if getattr(m, "tool_calls", None):
            d["tool_calls"] = [
                {"name": tc["name"], "args": tc.get("args")}
                for tc in m.tool_calls
            ]
    if isinstance(m, ToolMessage):
        d["tool_name"] = m.name
        if getattr(m, "status", None):
            d["status"] = m.status
    return d

def pretty_agent_output(out: dict):
    msgs = out.get("messages", [])
    compact = [msg_compact(m) for m in msgs]
    print(json.dumps(compact, indent=2))