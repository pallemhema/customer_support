import time

from schemas.supervisor_state_schema import (
    SupportState
)

from agents.tracking_agent import (
    tracking_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from helpers.extract_id import (
    extract_order_id
)

from agents.agent_retry import (
    stream_agent_with_retry
)


def tracking_node(
    state: SupportState
):

    start_time = time.time()
    print(
        "ENTER: tracking_node"
    )

    try:
        print(
            "Tracking Node execution"
        )

        query = state.get(

            "resolved_query",

            state[
                "query"
            ]

        )

        order_id = state.get(
            "order_id"
        )

        if not order_id:

            order_id = extract_order_id(
                query
            )

        prompt = f"""
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

        payload = {

            "messages":[

                (

                    "user",

                    prompt

                )

            ]

        }

        response = ""

        try:

            for event in stream_agent_with_retry(

                tracking_agent,

                payload,

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
                "Tracking failed:",
                e
            )

            response = """

Unable to retrieve tracking information.

Please try again later.

"""

        response = clean_llm_output(
            response
        )

        if not response.strip():

            response = """

Tracking information unavailable.

"""

        return {

            "order_id":
            order_id,

            "tracking_result":
            response,

            "response":
            response,
            "messages":[

        (

            "user",

            state["query"]

        ),

        (

            "assistant",

            response

        )

    ]
        }

    finally:
        elapsed = time.time() - start_time
        print(
            f"EXIT: tracking_node elapsed={elapsed:.3f}s"
        )