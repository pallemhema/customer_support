from agents.order_agent import order_agent
from helpers.clean_text import clean_llm_output
from schemas.supervisor_state_schema import SupportState
import re


def order_node(
state: SupportState
):

    print(
    "ORDER NODE EXECUTION"
    )


    query = state.get(
    "resolved_query",
    state["query"]
    )


    response = ""
    prompt = f"""

Customer ID:

{state["customer_id"]}

Customer Query:

{query}

MANDATORY:

For ALL tool calls send:

customer_id

Create order:
extract products
extract quantities

Cancel order:
extract order id

List orders:
send customer_id

Never ask customer again for customer id.

Perform order action immediately.

"""


    for chunk,meta in order_agent.stream(

    {

    "messages":[

    (

    "user",

    prompt

    )

    ]

    },

    stream_mode="messages"

    ):

        token = getattr(

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


        # remove reasoning

        response = re.sub(

        r"<think>.*?</think>",

        "",

        response,

        flags=re.DOTALL

        )


    output = clean_llm_output(
    response
    )


    print(
    "FINAL:",
    output
    )


    return {

    "response":
    output,

    "order_result":
    output,

    "messages":[

    (

    "user",

    state[
    "query"
    ]

    ),

    (

    "assistant",

    output

    )

    ]

    }