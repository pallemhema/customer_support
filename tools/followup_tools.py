from database.mongo import (
    followup_tickets_collection,
   
)

from datetime import (
    datetime,
    timedelta
)

from langchain_core.tools import tool

from schemas.followup_schemas import (
    ScheduleFollowupInput)

@tool(
args_schema=ScheduleFollowupInput
)

def schedule_followup(ticket_id:str,hours:int=24):

    """
    Schedule followup for ticket
    """

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

    followup_tickets_collection.update_one(

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

    "escalated_ticket_id":
    ticket_id,

    "followup_time":
    str(
        followup_time
    ),

    "status":
    "SCHEDULED"

    }
