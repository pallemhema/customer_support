from schemas.supervisor_state_schema import SupportState
from agents.escalation_agent import escalation_agent
from helpers.clean_text import clean_llm_output
from helpers.extract_id import extract_order_id
from langchain_core.messages import ToolMessage
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


    # ----------------
    # STREAM
    # ----------------

    response = ""


    for chunk,meta in escalation_agent.stream(

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


        response = re.sub(

        r"<think>.*?</think>",

        "",

        response,

        flags=re.DOTALL

        )


    final_output = clean_llm_output(
    response
    )


    print(
    "STREAM FINAL:",
    final_output
    )


    # ----------------
    # TOOL DATA ONLY
    # ----------------

    result = escalation_agent.invoke(

    {

    "messages":[

    (

    "user",

    prompt

    )

    ]

    }

    )


    ticket_id = None
    assigned_team = None
    status = None


    for msg in result[
    "messages"
    ]:

        if isinstance(
        msg,
        ToolMessage
        ):

            content = str(
            msg.content
            )


            ticket = re.search(

            r"'ticket_id':\s*'([^']+)'",

            content

            )


            team = re.search(

            r"'assigned_team':\s*'([^']+)'",

            content

            )


            stat = re.search(

            r"'status':\s*'([^']+)'",

            content

            )


            if ticket:

                ticket_id = ticket.group(
                1
                )


            if team:

                assigned_team = team.group(
                1
                )


            if stat:

                status = stat.group(
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
    status=="ESCALATED",

    "messages":[

    (
    "user",
    state["query"]
    ),

    (
    "assistant",
    final_output
    )

    ]

    }