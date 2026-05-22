from tools.helpers.get_order import (
    get_order
)

from tools.escalation.escalation_tools import *
from langchain_core.tools import tool

@tool
def handle_delivery(session_id,customer_id,order_id,intent,priority,query, ticket_id=None):
    """Handle delivery escalation"""
    actions=[]
    status=get_order(order_id)
    if not status:
        return {
         "response":"Order delivery details unavailable",
            "status":"ORDER_NOT_FOUND"
        }
    actions.append(
        f"Delivery status {status}"
    )

    if not ticket_id:
        ticket = create_ticket(session_id,intent,priority,customer_id,query)
        ticket_id = ticket["ticket_id"]
        actions.append("Ticket created")
    else:
        actions.appen("Existing ticket used")

    approval=request_hitl.invoke(
        "DELIVERY_INVESTIGATION",
        ticket["ticket_id"],
        "Can I raise delivery investigation?"
    )

    if not approval["approved"]:
        return {
            "response":"Investigation rejected",
            "status":"CANCELLED"
        }


    escalate_to_human(ticket["ticket_id"],"Logistics Team")

    return {
        "delivery_status":status,
        "ticket_id":ticket["ticket_id"],
        "assigned_team":"Logistics Team",
        "status":"ESCALATED",
        "actions":actions
    }