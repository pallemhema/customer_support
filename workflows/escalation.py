from schemas.supervisor_state_schema import (
SupportState
)

from agents.escalation_agent import (
escalation_agent
)

from helpers.clean_text import (
clean_llm_output
)
import re
from langchain_core.messages import ToolMessage
from helpers.extract_id import extract_order_id

def escalation_node(state: SupportState):

    print("Escalation Node Execution")

    query = state.get("resolved_query",state["query"])
    order_id = state.get("order_id")
    if not order_id:
        order_id = extract_order_id(query)

    result = escalation_agent.invoke(
    {
    "messages":[("user",f"""Customer ID:{state['customer_id']}
        Session ID:{state['session_id']}
        Order ID:{order_id}
        Intent:{state['intent']}
        Priority:{state['priority']}
        Query:{query}
        MANDATORY:
        Call matching escalation tool.
        Pass:
        session_id
        customer_id
        order_id
        intent
        priority
        query
        Return tool result only.

        """
)]})
    print("Escalation Result: ", result)

    final_output = ""
    ticket_id = None
    assigned_team = None
    status = None
    for msg in reversed(result["messages"]):
        content = getattr(msg,"content","")
        if content:
            final_output = clean_llm_output(content)
            break




   

    for msg in result["messages"]:

        print(
        "MESSAGE TYPE:",
        type(msg)
        )

        if isinstance(
            msg,
            ToolMessage
        ):

            content = msg.content

            print(
            "TOOL CONTENT:",
            content
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

    print(
    "ticket:",
    ticket_id
    )

    print(
    "team:",
    assigned_team
    )

    print(
    "status:",
    status
    )
    print("Escalation final output:", final_output)

    print("escalation Status: ", status)

    return {
        "order_id":order_id,
        "ticket_id":ticket_id,
        "assigned_team":assigned_team,
        "ticket_status":status,
        "response":final_output,
        "needs_followup":status == "ESCALATED",
        "messages":[
            ("user",state["query"]),
            ("assistant",final_output)
        ]
    }