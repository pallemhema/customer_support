from agents.order_agent import order_agent
from helpers.clean_text import clean_llm_output
from schemas.supervisor_state_schema import SupportState

def order_node(state:SupportState):
    
    query = state.get("resolved_query",state["query"])
    result = order_agent.invoke(

    {

    "messages":[("user",

    f"""

    Customer:

    {state["customer_id"]}

    Query:

    {query}

    Perform order action.

    """
    )]})

    output = ""

    for msg in reversed(
    result["messages"]
    ):

        content = getattr(
        msg,
        "content",
        ""
        )

        if content:

            output = clean_llm_output(
            content
            )

            break

    return {

    "response":
    output,

    "messages":[

    (
    "user",
    state["query"]
    ),

    (
    "assistant",
    output
    )

    ]

    }