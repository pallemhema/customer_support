from fastapi import FastAPI
from pydantic import BaseModel
from database.mongo import history_collection
from workflows.graph import support_graph
from langgraph.types import Command

app = FastAPI()


class ChatRequest(BaseModel):

    customer_id:str
    session_id:str
    thread_id:str
    query:str


class ResumeRequest(BaseModel):

    thread_id:str
    answer:str


@app.post("/chat")
def chat(data:ChatRequest):

    result = support_graph.invoke(

        {

        "customer_id":
        data.customer_id,

        "session_id":
        data.session_id,

        "thread_id":
        data.thread_id,

        "query":
        data.query

        },

        config={

        "configurable":{

        "thread_id":
        data.thread_id

        }

        }

    )

    print("chat result: ", result)

    return result

@app.post("/resume")
def resume(data:ResumeRequest):

    result = support_graph.invoke(

    Command(
    resume=data.answer
    ),

    config={

    "configurable":{

    "thread_id":
    data.thread_id

    }

    }

    )

    print(
    "Resume result:",
    result
    )


    response = {

    "response":
    result.get(
    "response"
    )

    }


    # IMPORTANT

    if "__interrupt__" in result:

        response[
        "__interrupt__"
        ] = result[
        "__interrupt__"
        ]


    return response
@app.get("/sessions/{customer_id}")
def get_sessions(customer_id:str):

    docs=[]

    rows = history_collection.find(
    {
        "customer_id":
        customer_id
    })

    for d in rows:

        title="New Chat"

        msgs = d.get(
            "messages",
            []
        )

        for m in msgs:

            if m["role"]=="user":

                title = m["content"]

                break

        docs.append({

        "session_id":
        d["session_id"],

        "thread_id":
        d["thread_id"],

        "updated_at":
        d.get(
            "updated_at"
        ),

        "title":
        title

        })

    docs.sort(

    key=lambda x:
    x["updated_at"],

    reverse=True

    )

    return docs

@app.get("/history/{thread_id}")
def get_history(thread_id:str):

    doc = history_collection.find_one(

        {

        "thread_id":
        thread_id

        }

    )

    if not doc:

        return {

        "messages":[]

        }
    

    return {

        "messages":
        doc.get(
            "messages",
            []
        )

    }