from schemas.supervisor_state_schema import (
SupportState
)

from agents.tracking_agent import (
tracking_agent
)

from helpers.clean_text import (
clean_llm_output
)

def tracking_node(
state:SupportState
):

    query = state.get(
        "resolved_query",
        state["query"]
    )

    result = tracking_agent.invoke({

        "messages":[(

        "user",

f"""
Customer:

{state["customer_id"]}

Order:

{state.get(
"order_id",
""
)}

Query:

{query}

Perform tracking.

Use tools.

"""
        )]

    })

    output = clean_llm_output(

        result[
        "messages"
        ][-1].content

    )

    print("Output: ", output)

    return {

        "tracking_result":
        output,

        "response":
        output,

        "messages":[

            (
                "assistant",
                output
            )

        ]
    }