from database.mongo import (
    escalation_tickets_collection
)

from datetime import datetime

from langgraph.types import interrupt
import uuid
from schemas.escalation_schemas import CreateActionRequestInput, CreateTicketInput, EscalateToHumanInput, RequestHITLInput



def create_ticket(session_id:str,intent:str,priority:str,customer_id:str, query:str):
    """
Create a new support ticket for a customer issue.

This tool generates a unique ticket ID and stores
issue information such as session ID, intent,
priority, description, status, timestamps,
and ticket history.

Args:
    session_id (str):
        Chat session associated with the issue.

    intent (str):
        Detected issue category such as
        refund_issue, payment_issue,
        login_issue, etc.

    priority (str):
        Severity level of the issue.

        Possible values:
        LOW
        MEDIUM
        HIGH
        CRITICAL

    Customer id (str):
        customer id

Returns:
    dict:
        Newly created ticket object.

Used By:
    Escalation Agent
    Follow-up Agent
"""
    print(f"Creating ticket for session {session_id} with intent {intent} and priority {priority}")

    ticket_id = str(uuid.uuid4())

    ticket = {

        "ticket_id":
        ticket_id,

        "customer_id":
        customer_id,

        "session_id":
        session_id,

        "intent":
        intent,

        "priority":
        priority,

        "status":
        "OPEN",
        "created_at":datetime.utcnow(),
        "updated_at":   datetime.utcnow(),
        }

  

    print(f"Generated ticket ID: {ticket_id}")

    print(f"Inserting ticket into database: {ticket}")

    escalation_tickets_collection.insert_one(ticket)

    return {
    "ticket_id":ticket_id,
    "session_id":session_id,
    "intent":intent,
    "priority":priority,
    "status":"OPEN"
}

def request_hitl(action,ticket_id,question):
    
    """ Pause graph execution and wait for customer approval. Customer replies: YES or NO"""
    interrupt_data = {

        "waiting_approval":
        True,

        "ticket_id":
        ticket_id,

        "action":
        action,

        "question":
        question,

        "options":[
        "YES",
        "NO"
        ]

    }
    approval = interrupt(interrupt_data)

    return {

    "waiting_approval":
    False,

    "resume_execution":
    True,

    "ticket_id":
    ticket_id,

    "approved":
    str(
    approval
    ).upper()=="YES",
    "__interrupt__":[
            interrupt_data
        ]

    }


def escalate_to_human(ticket_id:str,team="Support Team A"):
    """
Escalate a support ticket to a human support team.

Updates ticket ownership and changes
status to ESCALATED.

Examples:
    Fraud detection

    Critical payment issues

    Complex technical problems

Args:
    ticket_id (str):
        Ticket to escalate.

    team (str):
        Target support team.

        Default:
        Support Team A

Returns:
    dict:
        Escalation details including
        assigned team and status.

Used By:
    Escalation Agent
"""
    print(f"Escalating ticket {ticket_id} to {team}")

    result = escalation_tickets_collection.update_one({"ticket_id":ticket_id},
        {
            "$set":{
                "assigned_to":team,
                "status":"ESCALATED"
            }
        }
    )
    print(f"Ticket {ticket_id} escalated to {team}")


    

    return {
        "ticket_id":ticket_id,
        "assigned_team":team,
        "status":"ESCALATED"
    }

