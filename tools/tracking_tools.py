from langchain_core.tools import tool

from database.mongo import (
escalation_tickets_collection,
orders,


)
from tools.helpers.get_profile import get_profile
from tools.helpers.get_order import get_order
from tools.helpers.refund_tools import get_refund


@tool
def track_ticket(
ticket_id:str,
customer_id:str
):
    """
Track support ticket status.

Args:
    ticket_id:
        Support ticket identifier

    customer_id:
        Customer identifier

Returns:
    Ticket details including:
    status,
    assigned team,
    priority,
    issue type
    """

    ticket = escalation_tickets_collection.find_one(
    {
        "ticket_id":ticket_id,
        "customer_id":customer_id
    }
    )

    if not ticket:

        return {
            "status":"NOT_FOUND"
        }

    return {

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


@tool
def track_order(
order_id:str,
customer_id:str
):
    """
Track order delivery details.

Returns:

Order information

Delivery status

Courier details

Items purchased

Expected delivery

Shipping address
"""

    order = get_order(order_id,customer_id)

    if not order:

        return {
            "status":"NOT_FOUND",
            "order_id":order_id
        }

    return {

        "order_id":
        order["_id"],

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



@tool
def get_orders(
customer_id:str
):
    """
List all customer orders.

Returns:

order ids

delivery states

expected dates

totals
"""

    customer_orders = list(

        orders.find(
        {
            "customer_id":
            customer_id
        }
        )

    )

    if not customer_orders:

        return {
            "status":
            "NO_ORDERS"
        }

    result=[]

    for order in customer_orders:

        result.append(

        {

        "order_id":
        order["_id"],

        "delivery_status":
        order.get(
        "delivery_status"
        ),

        "expected_delivery":
        order.get(
        "expected_delivery"
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

        )

    return result

@tool
def get_customer_profile(customer_id:str):

    """Get customer profile details."""

    profile = get_profile(customer_id)

    return{
        "customer_id":customer_id,
        "name":profile.get("name"),
        "email":profile.get("email"),
        "phone":profile.get("phone"),
        "address":profile.get("address")
    }

@tool
def track_refund(
order_id:str,
customer_id:str
):
    """
Track refund status.

Returns:

refund amount

pending days

return completion

finance escalation

refund reason
"""

    refund = get_refund(order_id,customer_id)

    if not refund:

        return {
            "status":
            "NOT_FOUND"
        }

    return {

        "refund_id":
        refund.get(
        "_id"
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