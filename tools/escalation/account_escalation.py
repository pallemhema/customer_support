from tools.escalation.escalation_tools import *
from langchain_core.tools import tool
from tools.helpers.get_profile import get_profile
from langchain_core.tools import tool


@tool
def handle_account(
    session_id,
    customer_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    """
    Handle account security escalation.

    Uses customer profile:

    account status

    email verification

    last login

    before security actions.
    """

    actions = []

    profile = get_profile(customer_id)

    if not profile:

        return {

        "response":
        "Customer profile not found",

        "status":
        "PROFILE_NOT_FOUND"

        }

    actions.append(
        "Customer profile loaded"
    )

    account_status = profile.get(
        "account_status",
        "UNKNOWN"
    )

    email_verified = profile.get(
        "email_verified",
        False
    )

    last_login = profile.get(
        "last_login"
    )

    actions.append(
        f"Account status {account_status}"
    )

    actions.append(
        f"Email verified {email_verified}"
    )

    # existing ticket reuse

    if not ticket_id:

        ticket = create_ticket(
        

        session_id,

        intent,

        priority,

        customer_id,

        query

        
        )

        ticket_id = ticket[
            "ticket_id"
        ]

        actions.append(
            "New ticket created"
        )

    else:

        actions.append(
            "Existing ticket reused"
        )

    # critical cases

    suspicious = [

    "hacked",

    "unauthorized",

    "email changed",

    "password changed",

    "compromised",

    "login attempt"

    ]

    high_risk = any(
        x in query.lower()
        for x in suspicious
    )

    if high_risk:

        approval = request_hitl(
        

        "LOCK_ACCOUNT",

        ticket_id,

        f"""
Security issue detected.

Account:
{account_status}

Email verified:
{email_verified}

Last login:
{last_login}

Can I temporarily lock account?
"""

        
        )

        if not approval[
            "approved"
        ]:

            return {

            "response":
            "Account lock rejected by customer",

            "ticket_id":
            ticket_id,

            "status":
            "CANCELLED"

            }

        actions.append(
            "Customer approved lock"
        )

    escalate_to_human(
        ticket_id,

    
    "Security Team"

    
    )

    actions.append(
        "Escalated to Security Team"
    )

    return {

    "ticket_id":
    ticket_id,

    "assigned_team":
    "Security Team",

    "account_status":
    account_status,

    "email_verified":
    email_verified,

    "last_login":
    last_login,

    "status":
    "ESCALATED",

    "actions":
    actions

    }