from langchain_core.tools import tool

from database.mongo import (
    escalation_tickets_collection
)

from tools.helpers.get_profile import get_profile
from tools.helpers.get_order import get_order
from tools.helpers.refund_tools import get_refund
from tools.tool_retry import tool_with_retry


@tool
def track_ticket(
    ticket_id: str,
    customer_id: str
):
    """
    Track escalation/support ticket details.

    Args:
        ticket_id:
            Unique support ticket identifier.

        customer_id:
            Customer identifier.

    Returns:
        dict containing:

        status:
            SUCCESS / NOT_FOUND / FAILED

        data:
            ticket information including:

            ticket_id

            customer_id

            issue intent

            priority

            ticket status

            assigned team

            creation time
    """

    try:

        if escalation_tickets_collection is None:

            return {
                "status": "FAILED",
                "message": "Database unavailable"
            }

        ticket = tool_with_retry(

            escalation_tickets_collection.find_one,

            {
                "ticket_id": ticket_id,
                "customer_id": customer_id
            }
        )

        if not ticket:

            return {
                "status": "NOT_FOUND",
                "ticket_id": ticket_id
            }

        return {

            "status": "SUCCESS",

            "data": {

                "ticket_id":
                ticket.get(
                    "ticket_id"
                ),

                "customer_id":
                customer_id,

                "intent":
                ticket.get(
                    "intent"
                ),

                "priority":
                ticket.get(
                    "priority"
                ),

                "ticket_status":
                ticket.get(
                    "status"
                ),

                "assigned_team":
                ticket.get(
                    "assigned_to"
                ),

                "created_at":
                str(
                    ticket.get(
                        "created_at"
                    )
                )
            }
        }

    except Exception:

        return {

            "status": "FAILED",

            "message":
            "Ticket lookup failed"
        }


@tool
def track_order(
    order_id: str,
    customer_id: str
):
    """
    Track customer order details.

    Args:

        order_id:
            Order identifier.

        customer_id:
            Customer identifier.

    Returns:

        status:
            SUCCESS / NOT_FOUND / FAILED

        data:

            order details

            delivery status

            courier info

            tracking id

            expected delivery

            shipping address

            items

            amount
    """

    print("order id:", order_id)

    try:

        order = tool_with_retry(
            get_order,
            order_id,
            customer_id
        )

        if not order:

            return {

                "status":
                "NOT_FOUND",

                "order_id":
                order_id
            }

        return {

            "status":
            "SUCCESS",

            "data": {

                "order_id":
                str(
                    order.get(
                        "_id"
                    )
                ),

                "customer_id":
                customer_id,

                "delivery_status":
                order.get(
                    "delivery_status"
                ),

                "tracking_status":
                order.get(
                    "tracking_status"
                ),

                "courier":
                order.get(
                    "courier"
                ),

                "tracking_id":
                order.get(
                    "tracking_id"
                ),

                "expected_delivery":
                order.get(
                    "expected_delivery"
                ),

                "shipping_address":
                order.get(
                    "shipping_address"
                ),

                "items":
                order.get(
                    "items",
                    []
                ),

                "total_amount":
                order.get(
                    "total_amount"
                ),

                "currency":
                order.get(
                    "currency"
                )
            }
        }

    except Exception:

        return {

            "status":
            "FAILED",

            "message":
            "Order service unavailable"
        }


@tool
def get_customer_profile(
    customer_id: str
):
    """
    Get customer profile details.

    Args:

        customer_id:
            Customer identifier.

    Returns:

        status:
            SUCCESS / NOT_FOUND / FAILED

        data:

            customer name

            email

            phone

            address
    """

    try:
        print("customer id: ", customer_id)

        profile = tool_with_retry(
            get_profile,
            customer_id
        )
        print("profile:", profile)

        if not profile:

            return {

                "status":
                "NOT_FOUND",

                "customer_id":
                customer_id
            }

        return {

            "status":
            "SUCCESS",

            "data": {

                "customer_id":
                customer_id,

                "name":
                profile.get(
                    "name"
                ),

                "email":
                profile.get(
                    "email"
                ),

                "phone":
                profile.get(
                    "phone"
                ),

                "address":
                profile.get(
                    "address"
                )
            }
        }

    except Exception:

        return {

            "status":
            "FAILED",

            "message":
            "Customer lookup failed"
        }


@tool
def track_refund(
    order_id: str,
    customer_id: str
):
    """
    Track refund request details.

    Args:

        order_id:
            Order identifier.

        customer_id:
            Customer identifier.

    Returns:

        status:
            SUCCESS / NOT_FOUND / FAILED

        data:

            refund amount

            refund status

            pending days

            return completion

            escalation status

            refund reason
    """

    try:

        refund = tool_with_retry(
            get_refund,
            order_id,
            customer_id
        )

        if not refund:

            return {

                "status":
                "NOT_FOUND",

                "order_id":
                order_id
            }

        return {

            "status":
            "SUCCESS",

            "data": {

                "refund_id":
                str(
                    refund.get(
                        "_id"
                    )
                ),

                "order_id":
                order_id,

                "payment_id":
                refund.get(
                    "payment_id"
                ),

                "refund_requested":
                refund.get(
                    "refund_requested"
                ),

                "return_completed":
                refund.get(
                    "return_completed"
                ),

                "refund_status":
                refund.get(
                    "refund_status"
                ),

                "refund_amount":
                refund.get(
                    "refund_amount"
                ),

                "refund_days":
                refund.get(
                    "refund_days"
                ),

                "reason":
                refund.get(
                    "reason"
                ),

                "finance_escalated":
                refund.get(
                    "finance_escalated"
                ),

                "requested_at":
                str(
                    refund.get(
                        "requested_at"
                    )
                )
            }
        }

    except Exception:

        return {

            "status":
            "FAILED",

            "message":
            "Refund service unavailable"
        }