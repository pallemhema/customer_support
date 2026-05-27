from datetime import datetime
import uuid

from langchain_core.tools import tool
from langgraph.types import interrupt

from database.mongo import (
    escalation_tickets_collection
)

from schemas.escalation_schemas import (
    CreateTicketInput,
    RequestHITLInput,
    EscalateToHumanInput
)

from tools.tool_retry import (
    tool_with_retry
)


@tool(
    args_schema=
    CreateTicketInput
)
def create_ticket(
    session_id:str,
    intent:str,
    priority:str,
    customer_id:str,
    query:str
):

    """
    Create escalation ticket.

    Workflow:

    1. Generate ticket id

    2. Store issue

    3. Save escalation record

    Returns:

    SUCCESS

    FAILED

    ticket details
    """
    print("create ticket called")

    try:

        if escalation_tickets_collection is None:

            return {

                "status":
                "FAILED",

                "message":
                "Database unavailable"

            }

        ticket_id = str(
            uuid.uuid4()
        )

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

            "query":
            query,

            "status":
            "OPEN",

            "assigned_to":
            None,

            "created_at":
            datetime.utcnow(),

            "updated_at":
            datetime.utcnow()

        }

        tool_with_retry(

            escalation_tickets_collection.insert_one,

            ticket

        )

        return {

            "status":
            "SUCCESS",

            "data": {

                "ticket_id":
                ticket_id,

                "session_id":
                session_id,

                "customer_id":
                customer_id,

                "intent":
                intent,

                "priority":
                priority,

                "ticket_status":
                "OPEN"

            }

        }

    except Exception as e:

        print(
            "Ticket creation error:",
            e
        )

        return {

            "status":
            "FAILED",

            "message":
            "Ticket creation failed"

        }


@tool(
    args_schema=
    RequestHITLInput
)
def request_hitl(
    action:str,
    ticket_id:str,
    question:str
):

    """
    Human approval workflow.

    Supported:

    account lock

    refund access

    delivery investigation

    payment verification

    cancellation approval

    Returns:

    interrupt payload

    approval result
    """
    print("hitl called")


    interrupt_data = {

        "waiting_approval":
        True,

        "action":
        action,

        "ticket_id":
        ticket_id,

        "question":
        question,

        "options":[

            "YES",

            "NO"

        ]

    }

    approval = interrupt(
        interrupt_data
    )

    approved = (

        str(
            approval
        ).upper()

        ==

        "YES"

    )

    return {

        "status":
        "SUCCESS",

        "approved":
        approved,

        "resume_execution":
        True,

        "waiting_approval":
        False,

        "ticket_id":
        ticket_id,

        "__interrupt__":[

            interrupt_data

        ]

    }


@tool(
    args_schema=
    EscalateToHumanInput
)
def escalate_to_human(
    ticket_id:str,
    team:str="Support Team"
):

    """
    Escalate issue.

    Updates:

    assigned team

    ticket status

    Teams:

    Finance Team

    Security Team

    Logistics Team

    Payment Team

    Returns:

    SUCCESS

    NOT_FOUND

    FAILED
    """
    print("escalate to human called")


    try:

        if escalation_tickets_collection is None:

            return {

                "status":
                "FAILED",

                "message":
                "Database unavailable"

            }

        result = tool_with_retry(

            escalation_tickets_collection.update_one,

            {

                "ticket_id":
                ticket_id

            },

            {

                "$set":{

                    "assigned_to":
                    team,

                    "status":
                    "ESCALATED",

                    "updated_at":
                    datetime.utcnow()

                }

            }

        )

        if result.matched_count == 0:

            return {

                "status":
                "NOT_FOUND",

                "ticket_id":
                ticket_id

            }

        return {

            "status":
            "SUCCESS",

            "data": {

                "ticket_id":
                ticket_id,

                "assigned_team":
                team,

                "ticket_status":
                "ESCALATED"

            }

        }

    except Exception as e:

        print(
            "Escalation error:",
            e
        )

        return {

            "status":
            "FAILED",

            "message":
            "Escalation failed"

        }