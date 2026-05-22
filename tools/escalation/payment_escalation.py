from tools.helpers.payment_tools import (
get_payment
)

from tools.escalation.escalation_tools import *
from langchain_core.tools import tool

@tool
def handle_payment(session_id,customer_id,order_id,intent,priority,query,ticket_id=None):
    """Handle payment escalation"""

    actions=[]
    payment=get_payment( order_id,customer_id)

    if (not payment       or payment.get("status")=="NOT_FOUND"):
        return {
            "response": "Payment record not found",
            "status":"PAYMENT_NOT_FOUND"
        }
    
    actions.append("Payment loaded")
    actions.append(f"Payment status {payment.get('payment_status')}")
    if not ticket_id:
        ticket = create_ticket(session_id,intent,priority,customer_id,query)
        ticket_id = ticket["ticket_id"]
        actions.append("Ticket created")
    else:
        actions.appen("Existing ticket used")
    approval=request_hitl("ACCESS_PAYMENT",ticket["ticket_id"],"Can I access payment history?")
    
    if not approval["approved"]:
        return {
            "response":"Payment verification cancelled",
            "status":"CANCELLED"
        }

    escalate_to_human.invoke(ticket["ticket_id"],"Finance Team")

    return {
        "payment":payment,
        "ticket_id":ticket["ticket_id"],
        "assigned_team":"Finance Team",
        "status":"ESCALATED",
        "actions":actions
    }