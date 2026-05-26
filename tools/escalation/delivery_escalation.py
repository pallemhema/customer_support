from tools.helpers.get_order import (
    get_order
)

from tools.escalation.escalation_tools import *

from langchain_core.tools import tool

from tools.tool_retry import (
    tool_with_retry,
    tool_without_retry
)


@tool
def handle_delivery(
    session_id,
    customer_id,
    order_id,
    intent,
    priority,
    query,
    ticket_id=None
):
    """
    Handle delivery escalation.

    Retry allowed:

    get_order

    create_ticket

    escalate_to_human

    No retry:

    request_hitl

    Supports:

    delayed order

    missing delivery

    courier issues

    delivery investigation

    lost shipment

    Returns:

    SUCCESS

    FAILED

    ORDER_NOT_FOUND

    CANCELLED
    """

    return tool_without_retry(

        _handle_delivery,

        session_id,

        customer_id,

        order_id,

        intent,

        priority,

        query,

        ticket_id

    )


def _handle_delivery(
    session_id,
    customer_id,
    order_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    try:

        actions=[]

        status = tool_with_retry(

            get_order,

            order_id,

            customer_id

        )

        if (

            not status

            or

            status.get(
                "status"
            ) == "NOT_FOUND"

        ):

            return {

                "response":
                "Order delivery details unavailable",

                "status":
                "ORDER_NOT_FOUND"

            }

        actions.append(
            f"Delivery status {status}"
        )

        # --------------------
        # TICKET
        # --------------------

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

            if ticket.get(
                "status"
            ) != "SUCCESS":

                return ticket

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

        # --------------------
        # HITL
        # --------------------

        try:

            approval = request_hitl.invoke(

                {

                    "action":
                    "DELIVERY_INVESTIGATION",

                    "ticket_id":
                    ticket_id,

                    "question":

"""
Can I raise delivery investigation?
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
                "Investigation rejected",

                "status":
                "CANCELLED"

            }

        # --------------------
        # ESCALATE
        # --------------------

        escalation = tool_with_retry(

            escalate_to_human.invoke,

            {

                "ticket_id":
                ticket_id,

                "team":
                "Logistics Team"

            }

        )

        if escalation.get(
            "status"
        ) != "SUCCESS":

            return escalation

        actions.append(
            "Escalated to Logistics Team"
        )

        return {

            "delivery_status":
            status,

            "ticket_id":
            ticket_id,

            "assigned_team":
            "Logistics Team",

            "status":
            "ESCALATED",

            "actions":
            actions

        }

    except Exception as e:

        print(
            "DELIVERY ERROR:",
            e
        )

        # pass interrupt back

        if "Interrupt(" in str(e):

            raise

        return {

            "response":
            "Delivery workflow failed",

            "status":
            "FAILED"

        }