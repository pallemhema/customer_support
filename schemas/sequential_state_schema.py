from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


class SupportState(
    TypedDict
):

    query:str

    intent:str

    priority:str

    retrieved_docs:list

    response:str

    messages:Annotated[
        list,
        add_messages
    ]