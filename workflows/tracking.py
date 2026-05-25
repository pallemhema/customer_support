from schemas.supervisor_state_schema import (
SupportState
)

from agents.tracking_agent import (
tracking_agent
)

from helpers.clean_text import (
clean_llm_output
)
from schemas.supervisor_state_schema import SupportState
from agents.tracking_agent import tracking_agent
from helpers.extract_id import extract_order_id

def tracking_node(state: SupportState):

    print(
    "Tracking Node execution"
    )

    query = state.get(
        "resolved_query",
        state["query"]
    )

    order_id = state.get(
        "order_id"
    )

    if not order_id:

        order_id = extract_order_id(
        query
        )

    response=""


    for chunk,meta in tracking_agent.stream(

    {
        "messages":[
            (
            "user",

f"""
Customer ID:

{state["customer_id"]}

Order ID:

{order_id}

Customer Query:

{query}

MANDATORY:

Use tracking tool.

Do NOT ask again for customer id.

Do NOT ask again for order id.

Track immediately.

"""
            )
        ]
    },

    stream_mode="messages"

    ):

        token=getattr(
        chunk,
        "content",
        ""
        )

        if not token:
            continue

        print(
        "TOKEN:",
        token
        )

        response += token


    return {

        "order_id":
        order_id,

        "tracking_result":
        response,

        "response":
        response

    }