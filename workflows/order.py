from agents.order_agent import (
    order_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from schemas.supervisor_state_schema import (
    SupportState
)

from agents.agent_retry import (
    stream_agent_with_retry
)


def order_node(
    state: SupportState
):

    print(
        "ORDER NODE EXECUTION"
    )

    query = state.get(

        "resolved_query",

        state[
            "query"
        ]

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

Never ask customer again.

Perform action immediately.
"""

    try:

        for event in stream_agent_with_retry(

            order_agent,

            {

                "messages":[

                    (

                        "user",

                        prompt

                    )

                ]

            },

            stream_mode=
            "messages"

        ):

            chunk, meta = event

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

    except Exception as e:

            print(
                "Order node failed:",
                e
            )

            if "Interrupt(" in str(e):

                raise e

            return {

                "response":
                """
        Unable to process order request.

        Please retry.
        """
            }

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