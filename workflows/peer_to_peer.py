import sys
import os

from workflows.order import order_node

sys.path.append(
    os.path.abspath("..")
)

from langgraph.graph import StateGraph, START, END
from schemas.supervisor_state_schema import SupportState
from workflows.sequential import intent_node, retrieval_node, response_node
from workflows.escalation import escalation_node
from workflows.resolver import resolver_node
from workflows.followup import followup_node, followup_router
from langgraph.checkpoint.memory import MemorySaver
from workflows.tracking import tracking_node
from workflows.save_history import save_history
from workflows.supervisor import supervisor_node

def route_logic(state: SupportState):
    return state["route"]

memory = MemorySaver()

graph = StateGraph(SupportState)
graph.add_node("resolver",resolver_node)

graph.add_node("intent", intent_node)
graph.add_node("supervisor", supervisor_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("response", response_node)
graph.add_node("escalation", escalation_node)
graph.add_node("followup", followup_node)
graph.add_node("tracking", tracking_node)
graph.add_node("save_history",save_history)
graph.add_node("order",order_node)

graph.add_edge(START,"resolver")
graph.add_edge("resolver","intent")
graph.add_edge("intent", "supervisor")

graph.add_conditional_edges(
    "supervisor",
    route_logic,
    {

        "normal":"retrieval",

        "escalation":"escalation",

        "tracking":"tracking",
        "order":"order",

        "response":"response"

    }
)


graph.add_edge("response", END)
graph.add_conditional_edges(
    "escalation",
    followup_router,
    {
        "followup":"followup",
        "save_history":"save_history"
    }
)

graph.add_edge("retrieval", "response")
graph.add_edge("response","save_history")
graph.add_edge("followup","save_history")
graph.add_edge("tracking","save_history")
graph.add_edge("order","save_history")
graph.add_edge("save_history",END)




support_graph = graph.compile(checkpointer=memory)





