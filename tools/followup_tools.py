from datetime import (
    datetime,
    timedelta
)

from langchain_core.tools import tool

from database.mongo import (
    followup_tickets_collection
)

from schemas.followup_schemas import (
    ScheduleFollowupInput
)

from tools.tool_retry import (
    tool_with_retry
)


@tool(
    args_schema=
    ScheduleFollowupInput
)
def schedule_followup(
    ticket_id: str,
    hours: int = 24
):
    """
    Schedule follow up for an
    escalated support ticket.

    Creates or updates a followup
    entry in database.

    Args:

        ticket_id:

            Escalated ticket id.

        hours:

            Delay before followup.

            Default:
            24 hours

    Returns:

        SUCCESS

        FAILED

        Data includes:

            ticket id

            followup time

            followup status

            creation time

    Used By:

        Escalation Agent

        Followup Workflow

    Notes:

        Existing followups are updated.

        New followups use upsert.
    """

    try:

        if followup_tickets_collection is None:

            return {

                "status":
                "FAILED",

                "message":
                "Database unavailable"
            }

        followup_time = (

            datetime.utcnow()

            +

            timedelta(
                hours=hours
            )

        )

        data = {

            "escalated_ticket_id":
            ticket_id,

            "followup_at":
            followup_time,

            "status":
            "SCHEDULED",

            "created_at":
            datetime.utcnow()
        }

        tool_with_retry(

            followup_tickets_collection.update_one,

            {

                "escalated_ticket_id":
                ticket_id

            },

            {

                "$set":
                data

            },

            upsert=True

        )

        return {

            "status":
            "SUCCESS",

            "data": {

                "ticket_id":
                ticket_id,

                "followup_time":
                str(
                    followup_time
                ),

                "followup_status":
                "SCHEDULED",

                "created_at":
                str(
                    data[
                        "created_at"
                    ]
                )
            }
        }

    except Exception:

        return {

            "status":
            "FAILED",

            "message":
            "Followup scheduling failed"
        }