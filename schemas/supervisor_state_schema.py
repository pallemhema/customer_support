from typing import Optional, TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


class SupportState(
    TypedDict
):
    
    customer_id:str

    session_id:str

    thread_id:str

    # user input
    query:str
    resolved_query:str

    # intent node output
    intent:str

    priority:str

    route:str

    escalation:bool

    # retrieval
    retrieved_docs:list

    # response node
    response:str

    # customer info
    customer_id:str

    order_id:str

    # escalation
    ticket_id:str

    escalation_result:dict

    assigned_team:str

    ticket_status:str

    # approval
    approval_required:bool

    approval_status:str

    needs_followup:bool

    # follow_up
    followup:str

    last_order_id: Optional[str]

    last_topic: Optional[str]

    last_action: Optional[str]

    messages:Annotated[
        list,
        add_messages
    ]