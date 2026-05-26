from tools.helpers.refund_tools import (
    get_refund
)

from tools.escalation.escalation_tools import *

from langchain_core.tools import tool

from tools.tool_retry import (
    tool_with_retry,
    tool_without_retry
)


@tool
def handle_refund(
    session_id,
    customer_id,
    order_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    """
    Refund escalation workflow.

    Retry allowed:

    get_refund

    create_ticket

    escalate_to_human

    No retry:

    request_hitl
    """

    return tool_without_retry(

        _handle_refund,

        session_id,

        customer_id,

        order_id,

        intent,

        priority,

        query,

        ticket_id

    )


def _handle_refund(
    session_id,
    customer_id,
    order_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    actions=[]

    try:

        if not order_id:

            return {

                "response":
                "Order ID missing",

                "status":
                "FAILED"

            }

        refund = tool_with_retry(

            get_refund,

            order_id,

            customer_id

        )

        if (

            not refund

            or

            refund.get(
                "status"
            ) == "NOT_FOUND"

        ):

            return {

                "response":

f"""
No refund record found
for order {order_id}
""",

                "status":
                "REFUND_NOT_FOUND"

            }

        actions.append(
            "Refund loaded"
        )

        if not ticket_id:

            ticket = tool_with_retry(

                create_ticket.invoke,

                {

                    "session_id":
                    session_id,

                    "intent":
                    intent,

                    "priority":
                    priority,

                    "customer_id":
                    customer_id,

                    "query":
                    query

                }

            )

            ticket_id = ticket[
                "data"
            ][
                "ticket_id"
            ]

            actions.append(
                "Ticket created"
            )

        else:

            actions.append(
                "Existing ticket used"
            )

        refund_amount = refund.get(
            "refund_amount",
            0
        )

        if refund_amount < 5000:

            try:

                approval = request_hitl.invoke(

                    {

                        "action":
                        "ACCESS_REFUND",

                        "ticket_id":
                        ticket_id,

                        "question":

"""
Can I access refund history?
"""

                    }

                )

            except Exception as e:

                if "Interrupt(" in str(e):

                    raise

                raise

            if not approval.get(
                "approved",
                False
            ):

                return {

                    "response":
                    "Refund verification cancelled",

                    "ticket_id":
                    ticket_id,

                    "status":
                    "CANCELLED"

                }

            actions.append(
                "Customer approved"
            )

        escalation = tool_with_retry(

            escalate_to_human.invoke,

            {

                "ticket_id":
                ticket_id,

                "team":
                "Finance Team"

            }

        )

        actions.append(
            "Finance escalation"
        )

        return {

            "refund":
            refund,

            "ticket_id":
            ticket_id,

            "assigned_team":
            "Finance Team",

            "status":
            "ESCALATED",

            "actions":
            actions,

            "response":

f"""
Refund issue escalated

Ticket:

{ticket_id}

Team:

Finance Team

Refund Status:

{refund.get('refund_status')}

Amount:

₹{refund.get('refund_amount')}
"""

        }

    except Exception as e:

        print(
            "REFUND ERROR:",
            e
        )

        if "Interrupt(" in str(e):

            raise

        return {

            "response":
            "Refund workflow failed",

            "status":
            "FAILED"

        }