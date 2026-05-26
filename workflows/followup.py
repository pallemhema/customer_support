from schemas.supervisor_state_schema import (
    SupportState
)

from agents.followup_agent import (
    followup_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from agents.agent_retry import (
    stream_agent_with_retry
)


def followup_node(
    state: SupportState
):

    print(
        "Followup Node Execution"
    )

    print(
        state
    )

    ticket_id = state.get(
        "ticket_id"
    )

    if not ticket_id:

        return {

            "followup":
            None,

            "needs_followup":
            False
        }

    escalation_response = state.get(

        "response",

        ""

    )

    prompt = f"""
Ticket:

{ticket_id}

Schedule followup.

Do not create ticket.

Existing escalation response:

{escalation_response}
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

            followup_agent,

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
            "Followup failed:",
            e
        )

        return {

            "followup":
            None,

            "needs_followup":
            False,

            "response":

            state.get(
                "response",
                ""
            ),

            "messages":[

                (

                    "user",

                    state[
                        "query"
                    ]

                ),

                (

                    "assistant",

                    state.get(
                        "response",
                        ""
                    )

                )

            ]
        }

    output = clean_llm_output(
        response
    )

    print(
        "FOLLOWUP FINAL:",
        output
    )

    final_response = f"""
{escalation_response}

{output}
"""

    return {

        "followup":
        output,

        "needs_followup":
        False,

        "response":
        final_response,

        "messages":[

            (

                "user",

                state[
                    "query"
                ]

            ),

            (

                "assistant",

                final_response

            )

        ]
    }


def followup_router(
    state
):

    print(
        "Graph state at followup router:",
        state
    )

    if state.get(

        "needs_followup",

        False

    ):

        return "followup"

    return "save_history"