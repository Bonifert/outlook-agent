from langgraph.graph import StateGraph, START, END

from nodes.classify import classify_meetings_node, classify_with_llm_node
from nodes.info_requests import info_request_node
from nodes.mailbox import get_outlook_data_node, move_emails_to_processing_node, move_emails_to_done_node
from nodes.summary import summary_node
from state import AgentState


graph = StateGraph(AgentState)
graph.add_node("fetch", get_outlook_data_node)
graph.add_node("move_to_processing", move_emails_to_processing_node)
graph.add_node("move_to_done", move_emails_to_done_node)
graph.add_node("classify_meetings", classify_meetings_node)
graph.add_node("classify_with_llm", classify_with_llm_node)
graph.add_node("extract_info_requests", info_request_node)
graph.add_node("summarize", summary_node)

graph.add_edge(START, "fetch")
graph.add_edge("fetch", "move_to_processing")
graph.add_edge("move_to_processing", "classify_meetings")
graph.add_edge("classify_meetings", "classify_with_llm")
graph.add_edge("classify_with_llm", "extract_info_requests")
graph.add_edge("classify_with_llm", "summarize")
# TODO: missing meeting summarization

# graph.add_edge("move_to_done", END)

app = graph.compile()

with open("./graph-png/graph.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())