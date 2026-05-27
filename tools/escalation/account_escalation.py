from langchain_core.tools import tool

from tools.escalation.escalation_tools import (
    create_ticket,
    request_hitl,
    escalate_to_human
)

from tools.helpers.get_profile import (
    get_profile
)

from tools.tool_retry import (
    tool_with_retry,
    tool_without_retry
)


@tool
def handle_account(
    session_id:str,
    customer_id:str,
    intent:str,
    priority:str,
    query:str,
    ticket_id:str=None
):

    """
    Account security escalation workflow.

    Supports:

    hacked account

    email changed

    password changed

    unauthorized access

    suspicious login

    compromised account

    Retry allowed:

    get_profile

    create_ticket

    escalate_to_human

    No retry:

    request_hitl

    Returns:

    SUCCESS

    FAILED

    PROFILE_NOT_FOUND

    CANCELLED
    """

    return tool_without_retry(

        _handle_account,

        session_id,

        customer_id,

        intent,

        priority,

        query,

        ticket_id

    )


def _handle_account(
    session_id,
    customer_id,
    intent,
    priority,
    query,
    ticket_id=None
):

    actions = []

    try:

        # -------------------
        # PROFILE
        # -------------------

        profile = tool_with_retry(

            get_profile,

            customer_id

        )

        if not profile:

            return {

                "status":
                "PROFILE_NOT_FOUND",

                "response":
                "Customer profile unavailable"

            }

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
            "Profile loaded"
        )

        # -------------------
        # CREATE TICKET
        # -------------------

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
                "Existing ticket reused"
            )

        # -------------------
        # RISK CHECK
        # -------------------

        suspicious = [

            "hacked",

            "hack",

            "unauthorized",

            "email changed",

            "email was changed",

            "password changed",

            "password reset",

            "compromised",

            "suspicious login",

            "login attempt",

            "without my permission",

            "someone accessed",

            "email modified"

        ]

        query_text = query.lower()

        high_risk = any(

            word in query_text

            for word in suspicious

        )

        print(
            "RISK:",
            high_risk
        )

        # -------------------
        # HITL
        # -------------------

        if high_risk:

            try:

                approval = request_hitl.invoke(

                    {

                        "action":
                        "LOCK_ACCOUNT",

                        "ticket_id":
                        ticket_id,

                        "question":

f"""
Security issue detected

Account:

{account_status}

Email Verified:

{email_verified}

Last Login:

{last_login}

Lock account temporarily?
"""

                    }

                )

            except Exception as e:

                if "Interrupt(" in str(e):

                    raise e

                raise e

            if not approval.get(
                "approved",
                False
            ):

                return {

                    "status":
                    "CANCELLED",

                    "ticket_id":
                    ticket_id,

                    "message":
                    "Account lock rejected"

                }

            actions.append(
                "Customer approved lock"
            )

        # -------------------
        # ESCALATION
        # -------------------

        escalation = tool_with_retry(

            escalate_to_human.invoke,

            {

                "ticket_id":
                ticket_id,

                "team":
                "Security Team"

            }

        )

        if escalation.get(
            "status"
        ) != "SUCCESS":

            return escalation

        actions.append(
            "Escalated to Security Team"
        )

        # -------------------
        # SUCCESS
        # -------------------

        return {

            "status":
            "SUCCESS",

            "ticket_id":
            ticket_id,

            "assigned_team":
            "Security Team",

            "account_status":
            account_status,

            "email_verified":
            email_verified,

            "last_login":
            str(
                last_login
            ),

            "ticket_status":
            "ESCALATED",

            "actions":
            actions

        }

    except Exception as e:

        print(
            "ACCOUNT ERROR:",
            e
        )

        # pass HITL back to graph

        if "Interrupt(" in str(e):

            raise

        return {

            "status":
            "FAILED",

            "response":
            "Account workflow failed"

        }
