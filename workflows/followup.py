

from schemas.supervisor_state_schema import (
SupportState
)

from agents.followup_agent import (
followup_agent
)

from helpers.clean_text import (
clean_llm_output
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
        None

        }

    escalation_response = state.get(
        "response",
        ""
    )

    result = followup_agent.invoke(
    {

    "messages":[

    (

    "user",

f"""

Ticket:

{ticket_id}

Schedule followup.

Do not create ticket.

Existing escalation response:

{escalation_response}

"""

    )

    ]

    }

    )

    output = clean_llm_output(

    result[
    "messages"
    ][-1].content

    )

    final_response = f"""

{escalation_response}

{output}

"""

    return {

    "followup":
    output,

    "response":
    final_response,

    "messages":[

    (
    "user",
    state["query"]
    ),

    (
    "assistant",
    final_response
    )

    ]

    }

def followup_router(state):

    print("Graph state at followup router: ", state)

    if state.get(
        "needs_followup",
        False
    ):

        return "followup"

    return "save_history"