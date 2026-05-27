from fastapi import FastAPI
from pydantic import BaseModel
from database.mongo import history_collection
from workflows.graph import support_graph
from langgraph.types import Command
from fastapi.responses import StreamingResponse
import json
from fastapi.responses import StreamingResponse
from langchain_core.messages import (
    HumanMessage,
    AIMessage
)


app = FastAPI()


class ChatRequest(BaseModel):

    customer_id:str
    session_id:str
    thread_id:str
    query:str


class ResumeRequest(BaseModel):

    thread_id:str
    answer:str


@app.post("/chat-stream")
def chat_stream(data: ChatRequest):

    # ----------------------
    # LOAD HISTORY
    # ----------------------

    history_doc = history_collection.find_one(
        {
            "thread_id":
            data.thread_id
        }
    )

    history = []

    if history_doc:

        msgs = history_doc.get(
            "messages",
            []
        )

        for msg in msgs:

            role = msg.get(
                "role"
            )

            content = msg.get(
                "content",
                ""
            )

            if role == "user":

                history.append(

                    HumanMessage(
                        content=content
                    )

                )

            elif role == "assistant":

                history.append(

                    AIMessage(
                        content=content
                    )

                )

    print(
        "TOTAL HISTORY:",
        len(history)
    )

    # graph memory only

    graph_history = history[-4:]

    print(
        "GRAPH HISTORY:",
        len(graph_history)
    )

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
                data.query,

                "messages":
                graph_history

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
        try:

            for mode, chunk in stream:

                # ----------------
                # TOKEN STREAM
                # ----------------

                if mode == "messages":

                    msg, meta = chunk

                    node = meta.get(
                        "langgraph_node",
                        ""
                    )

                    hidden = [

                        "resolver",

                        "intent",

                        "supervisor",

                        "save_history"

                    ]

                    if node in hidden:

                        continue

                    token = getattr(

                        msg,

                        "content",

                        ""

                    )

                    if not token:

                        continue

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

                # ----------------
                # NODE UPDATES
                # ----------------

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
        except Exception as e:

            print(
                "STREAM ERROR:",
                e
            )

            yield (

                json.dumps({

                    "type":
                    "error",

                    "message":

                    """
        Sorry.

        The assistant temporarily hit a model limit.

        Retrying failed and response generation stopped.

        Please try again in a moment.
        """

                })

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

@app.delete("/session/{thread_id}")
def delete_session(thread_id:str):

    result = history_collection.delete_one(
        {
            "thread_id":
            thread_id
        }
    )

    if result.deleted_count == 0:

        return {

            "status":
            "NOT_FOUND",

            "message":
            "Session not found"

        }

    return {

        "status":
        "SUCCESS",

        "thread_id":
        thread_id,

        "message":
        "Session deleted"

    }