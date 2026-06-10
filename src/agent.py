from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import supervisor_node, query_node, analysis_node, writer_node


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("query_agent", query_node)
    workflow.add_node("analysis_agent", analysis_node)
    workflow.add_node("writer_agent", writer_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "query_agent": "query_agent",
            "analysis_agent": "analysis_agent",
            "writer_agent": "writer_agent",
            "END": END,
        },
    )

    workflow.add_edge("query_agent", "supervisor")
    workflow.add_edge("analysis_agent", "supervisor")
    workflow.add_edge("writer_agent", "supervisor")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
