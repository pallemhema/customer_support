from agents.response_agent import (
    response_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from agents.agent_retry import (
    stream_agent_with_retry
)


def response_node(
    state
):

    print(
        "RESPONSE NODE EXECUTION"
    )

    text = ""

    if state.get(
        "intent"
    ) == "greeting_intent":

        text += f"""
Customer greeting detected

Customer message:

{state['query']}

Respond warmly.

Keep response short.
"""

    if state.get(
        "retrieved_docs"
    ):

        text += "\n"

        text += str(

            state[
                "retrieved_docs"
            ]

        )

    if state.get(
        "escalation_result"
    ):

        text += "\n"

        text += str(

            state[
                "escalation_result"
            ]

        )

    if state.get(
        "followup"
    ):

        text += "\n"

        text += str(

            state[
                "followup"
            ]

        )

    prompt = f"""
Customer Query:

{state['query']}

Context:

{text}

Generate response
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

            response_agent,

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
            "Response failed:",
            e
        )

        response = """

Sorry.

Unable to generate response now.

Please try again.

"""

    response = clean_llm_output(
        response
    )

    if not response.strip():

        response = """

No response generated.

Please retry.

"""

    print(
        "FINAL:",
        response
    )

    return {

        "response":
        response,

        "messages":[

            (

                "user",

                state[
                    "query"
                ]

            ),

            (

                "assistant",

                response

            )

        ]
    }