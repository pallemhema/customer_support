from datetime import datetime
from schemas.supervisor_state_schema import SupportState
from database.mongo import history_collection

from datetime import datetime

def save_history(
state
):

    # interrupt phase
    if state.get(
    "waiting_approval"
    ):

        print(
        "skip interrupt save"
        )

        return {}

    # resume phase
    if state.get(
    "resume_execution"
    ):

        print(
        "resume detected"
        )

        existing = history_collection.find_one(
        {
        "thread_id":
        state["thread_id"]
        }
        )

        if existing:

            msgs = existing.get(
            "messages",
            []
            )

            if msgs:

                last_user = None

                for m in reversed(
                msgs
                ):

                    if m[
                    "role"
                    ]=="user":

                        last_user=m

                        break

                if (

                last_user

                and

                last_user[
                "content"
                ]==state[
                "query"
                ]

                ):

                    print(
                    "duplicate skipped"
                    )

                    return {}

    

    history_collection.update_one(

        {
            "thread_id":
            state["thread_id"]
        },

        {

        "$push":{

            "messages":{

                "$each":[

                {

                "role":"user",

                "content":
                state["query"],

                "intent":
                state.get(
                    "intent"
                ),

                "route":
                state.get(
                    "route"
                ),

                "time":
                datetime.utcnow()

                },

                {

                "role":"assistant",

                "content":
                state.get(
                    "response"
                ),

                "time":
                datetime.utcnow()

                }

                ]

            }

        },

        "$set":{

        "updated_at":
        datetime.utcnow(),

        "customer_id":
        state["customer_id"],

        "session_id":
        state["session_id"]

        },

        "$setOnInsert":{

        "created_at":
        datetime.utcnow()

        }

        },

        upsert=True

    )

    return {}