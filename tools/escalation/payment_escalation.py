from tools.helpers.payment_tools import (
    get_payment
)

from tools.escalation.escalation_tools import *

from langchain_core.tools import tool

from tools.tool_retry import (
    tool_with_retry,
    tool_without_retry
)


@tool
def handle_payment(
    session_id,
    customer_id,
    order_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    """
    Handle payment escalation.

    Retry allowed:

    get_payment

    create_ticket

    escalate_to_human

    No retry:

    request_hitl
    """

    return tool_without_retry(

        _handle_payment,

        session_id,

        customer_id,

        order_id,

        intent,

        priority,

        query,

        ticket_id

    )


def _handle_payment(
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

        payment = tool_with_retry(

            get_payment,

            order_id

        )

        if (

            not payment

            or

            payment.get(
                "status"
            ) == "NOT_FOUND"

        ):

            return {

                "response":
                "Payment record not found",

                "status":
                "PAYMENT_NOT_FOUND"

            }

        actions.append(
            "Payment loaded"
        )

        actions.append(

            f"Payment status {payment.get('payment_status')}"

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

        try:

            approval = request_hitl.invoke(

                {

                    "action":
                    "ACCESS_PAYMENT",

                    "ticket_id":
                    ticket_id,

                    "question":

"""
Can I access payment history?
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
                "Payment verification cancelled",

                "status":
                "CANCELLED"

            }

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

            "payment":
            payment,

            "ticket_id":
            ticket_id,

            "assigned_team":
            "Finance Team",

            "status":
            "ESCALATED",

            "actions":
            actions

        }

    except Exception as e:

        print(
            "PAYMENT ERROR:",
            e
        )

        if "Interrupt(" in str(e):

            raise

        return {

            "response":
            "payment workflow failed",

            "status":
            "FAILED"

        }