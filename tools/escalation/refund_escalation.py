from tools.helpers.refund_tools import get_refund
from tools.escalation.escalation_tools import *

from langchain_core.tools import tool


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

    """Handle refund escalation workflow"""

    actions=[]

    if not order_id:
        return {
        "response":"Order ID missing",
        "status":"FAILED"
        }

    refund = get_refund(order_id,customer_id)


    if (not refund or refund.get("status")=="NOT_FOUND"):
        return {
        "response":f"No refund record found for order {order_id}",
        "status":"REFUND_NOT_FOUND"
        }

    actions.append("Refund record loaded")
    if not ticket_id:
        ticket = create_ticket(session_id,intent,priority,customer_id,query)
        ticket_id = ticket["ticket_id"]
        actions.append("Ticket created")
    else:
        actions.appen("Existing ticket used")

    
    actions.append(
    "Ticket created"
    )


    refund_amount = refund.get("refund_amount", 0)


    if refund_amount < 50000:
        approval = request_hitl("ACCESS_REFUND",ticket["ticket_id"],"Can I access refund history?")

        if not approval["approved"]:
            return {
            "response":"Refund verification cancelled by customer",
            "ticket_id":ticket["ticket_id"],
            "status":"CANCELLED"
            }
        actions.append("Customer approved")

    escalate = escalate_to_human(ticket["ticket_id"],"Finance Team")
    print("esclate to human output:", escalate)

    actions.append("Finance escalation")

    return {
        "refund":refund,
        "ticket_id":ticket["ticket_id"],
        "assigned_team":escalate["assigned_team"],
        "status":escalate["status"],
        "actions":actions,
        "response":f"""
            Refund issue escalated.
            Ticket:{ticket['ticket_id']}

            Team:Finance Team

            Refund Status:{refund.get('refund_status')}
            Amount:₹{refund.get('refund_amount')}
            """

    }