from fastapi import FastAPI
from pydantic import BaseModel
from database.mongo import history_collection
from workflows.graph import support_graph
from langgraph.types import Command
from agents.escalation_agent import escalation_agent
from agents.response_agent  import response_agent
from agents.order_agent import order_agent
from agents.tracking_agent import tracking_agent

app = FastAPI()


class ChatRequest(BaseModel):

    customer_id:str
    session_id:str
    thread_id:str
    query:str


class ResumeRequest(BaseModel):

    thread_id:str
    answer:str

from fastapi.responses import StreamingResponse
import json

from fastapi.responses import StreamingResponse
import json
import re

@app.post("/chat-stream")
def chat_stream(
data: ChatRequest
):

    def generate():

        stream = support_graph.stream(

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

        },

        stream_mode=[

        "messages",

        "updates"

        ]

        )


        for mode,chunk in stream:


            # ------------------
            # TOKEN STREAM
            # ------------------

            if mode == "messages":

                msg,meta = chunk

                token = getattr(
                msg,
                "content",
                ""
                )

                if not token:

                    continue


                token = re.sub(

                r"<think>.*?</think>",

                "",

                token,

                flags=re.DOTALL

                ).strip()


                if token:

                    yield (

                    json.dumps({

                    "type":
                    "token",

                    "token":
                    token

                    })

                    +

                    "\n"

                    )


            # ------------------
            # NODE UPDATES
            # ------------------

            elif mode == "updates":

                if "__interrupt__" in chunk:

                    yield (

                    json.dumps({

                    "type":
                    "interrupt",

                    "data":
                    chunk[
                    "__interrupt__"
                    ]

                    },

                    default=str

                    )

                    +

                    "\n"

                    )

                else:

                    yield (

                    json.dumps({

                    "type":
                    "update",

                    "data":
                    chunk

                    },

                    default=str

                    )

                    +

                    "\n"

                    )


    return StreamingResponse(

    generate(),

    media_type=
    "text/event-stream"

    )
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

