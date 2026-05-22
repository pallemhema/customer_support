from database.mongo import sessions_collection
import uuid
def create_session(
        customer_id
):

    session_id = str(
        uuid.uuid4()
    )

    thread_id = (

        f"{customer_id}_"

        f"{session_id}"

    )

    sessions_collection.insert_one(
    {

        "customer_id":
        customer_id,

        "session_id":
        session_id,

        "thread_id":
        thread_id,

        "status":
        "ACTIVE"
    }
    )

    return {

        "customer_id":
        customer_id,

        "session_id":
        session_id,

        "thread_id":
        thread_id
    }

