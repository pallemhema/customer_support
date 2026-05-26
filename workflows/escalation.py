from schemas.supervisor_state_schema import (
    SupportState
)

from agents.escalation_agent import (
    escalation_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from helpers.extract_id import (
    extract_order_id
)

from langchain_core.messages import (
    ToolMessage
)

from agents.agent_retry import (
    stream_agent_with_retry
)

import re


def escalation_node(
    state: SupportState
):

    print(
        "Escalation Node Execution"
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

    prompt = f"""
Customer ID:
{state['customer_id']}

Session ID:
{state['session_id']}

Order ID:
{order_id}

Intent:
{state['intent']}

Priority:
{state['priority']}

Query:
{query}

MANDATORY:

Call matching escalation tool.

Return tool result only.
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

    tool_messages = []

    try:

        for event in stream_agent_with_retry(

            escalation_agent,

            payload,

            stream_mode="messages"

        ):

            chunk, meta = event

            if isinstance(
                chunk,
                ToolMessage
            ):

                tool_messages.append(
                    chunk
                )

                continue

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

            response = re.sub(

                r"<think>.*?</think>",

                "",

                response,

                flags=re.DOTALL

            )

    except Exception as e:

        print(
            "Escalation stream failed:",
            e
        )

        # IMPORTANT

        if "Interrupt(" in str(e):

            raise e

        return {

            "ticket_status":
            "FAILED",

            "response":
            "Escalation failed"

        }

        return {

            "order_id":
            order_id,

            "ticket_id":
            None,

            "assigned_team":
            None,

            "ticket_status":
            "FAILED",

            "response":
            "Escalation failed",

            "needs_followup":
            False,

            "messages":[

                (

                    "user",

                    state[
                        "query"
                    ]

                ),

                (

                    "assistant",

                    "Escalation failed"

                )

            ]
        }

    final_output = clean_llm_output(
        response
    )

    print(
        "STREAM FINAL:",
        final_output
    )

    ticket_id = None

    assigned_team = None

    status = None

    for msg in tool_messages:

        content = str(
            msg.content
        )

        ticket_match = re.search(

            r"'ticket_id':\s*'([^']+)'",

            content

        )

        team_match = re.search(

            r"'assigned_team':\s*'([^']+)'",

            content

        )

        status_match = re.search(

            r"'status':\s*'([^']+)'",

            content

        )

        if ticket_match:

            ticket_id = ticket_match.group(
                1
            )

        if team_match:

            assigned_team = team_match.group(
                1
            )

        if status_match:

            status = status_match.group(
                1
            )

    return {

        "order_id":
        order_id,

        "ticket_id":
        ticket_id,

        "assigned_team":
        assigned_team,

        "ticket_status":
        status,

        "response":
        final_output,

        "needs_followup":

        status == "ESCALATED",

        "messages":[

            (

                "user",

                state[
                    "query"
                ]

            ),

            (

                "assistant",

                final_output

            )

        ]

    }