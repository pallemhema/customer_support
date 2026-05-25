
import streamlit as st
import requests
import uuid
import ast
import re
import json
from requests.exceptions import ChunkedEncodingError

API = "http://localhost:8000"

st.set_page_config(
page_title="Customer Support",
layout="wide"
)

# --------------------------------
# SESSION STATE
# --------------------------------

defaults = {

"customer_id":"cust001",

"last_customer":"cust001",

"session_id":str(
uuid.uuid4()
),

"messages":[],

"interrupt":None,

"loading":False,

"processing":False,

"show_loading_message":False

}

for k,v in defaults.items():

    if k not in st.session_state:

        st.session_state[k]=v


if "thread_id" not in st.session_state:

    st.session_state.thread_id=(

    f"{st.session_state.customer_id}_"

    f"{st.session_state.session_id}"

    )



# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.title(
    "🛎 Customer Support"
    )

    customer=st.text_input(
    "Customer ID",
    st.session_state.customer_id
    )


    # CUSTOMER CHANGE

    if customer != st.session_state.last_customer:

        st.session_state.last_customer=customer

        st.session_state.customer_id=customer

        st.session_state.messages=[]

        st.session_state.interrupt=None

        st.session_state.processing=False

        st.session_state.loading=False

        try:

            sessions=requests.get(
f"{API}/sessions/{customer}"
            ).json()

        except:

            sessions=[]


        if sessions:

            latest=sessions[0]

            st.session_state.session_id=(

            latest[
            "session_id"
            ]

            )

            st.session_state.thread_id=(

            latest[
            "thread_id"
            ]

            )

            history=requests.get(

f"{API}/history/{latest['thread_id']}"

            ).json()

            st.session_state.messages=(

            history.get(
            "messages",
            []
            )

            )

        else:

            sid=str(
            uuid.uuid4()
            )

            st.session_state.session_id=sid

            st.session_state.thread_id=(

            f"{customer}_{sid}"

            )

        st.rerun()


    if st.button(
    "➕ New Chat",
    use_container_width=True
    ):

        sid=str(
        uuid.uuid4()
        )

        st.session_state.session_id=sid

        st.session_state.thread_id=(

        f"{customer}_{sid}"

        )

        st.session_state.messages=[]

        st.session_state.interrupt=None

        st.session_state.processing=False

        st.session_state.loading=False

        st.rerun()


    st.divider()

    st.subheader(
    "💬 Sessions"
    )

    try:

        sessions=requests.get(
f"{API}/sessions/{customer}"
        ).json()

    except:

        sessions=[]


    for s in sessions:

        label=s.get(
        "title",
        "New Chat"
        )

        if len(label)>35:

            label=label[:35]+"..."

        if st.button(
        label,
        key=s["thread_id"]
        ):

            history=requests.get(

f"{API}/history/{s['thread_id']}"

            ).json()

            st.session_state.thread_id=s[
            "thread_id"
            ]

            st.session_state.session_id=s[
            "session_id"
            ]

            st.session_state.messages=(

            history.get(
            "messages",
            []
            )

            )

            st.session_state.interrupt=None

            st.rerun()


# --------------------------------
# CHAT
# --------------------------------

st.title(
"🤖 Customer Support Assistant"
)

for msg in st.session_state.messages:

    with st.chat_message(
    msg["role"]
    ):

        st.markdown(
        msg["content"]
        )






# --------------------------------
# INPUT
# --------------------------------

disabled=(

st.session_state.processing

or

st.session_state.interrupt
is not None

)

query=st.chat_input(

" Thinking..."

if disabled

else

"Ask something...",

disabled=disabled

)


# --------------------------------
# SEND QUERY
# --------------------------------

if query:

    st.session_state.messages.append({

    "role":
    "user",

    "content":
    query

    })

    st.session_state.pending_query=query

    st.session_state.processing=True

    st.session_state.loading=True

    st.session_state.show_loading_message=True

    st.rerun()



# --------------------------------
# PROCESS QUERY
# --------------------------------

if (

st.session_state.processing

and

"pending_query"
in st.session_state

):

    query = st.session_state.pending_query

    del st.session_state.pending_query


    with st.chat_message(
    "assistant"
    ):

        thinking = st.empty()

        thinking.markdown(
        "Thinking..."
        )

        holder = st.empty()

        final = ""


        try:

            response = requests.post(

            f"{API}/chat-stream",

            json={

            "customer_id":
            st.session_state.customer_id,

            "session_id":
            st.session_state.session_id,

            "thread_id":
            st.session_state.thread_id,

            "query":
            query

            },

            stream=True

            )


            for line in response.iter_lines():

                if not line:

                    continue


                payload = json.loads(
                line.decode()
                )


                kind = payload.get(
                "type"
                )


                # -----------------
                # TOKEN STREAM
                # -----------------
                if kind == "token":

                    print("kind:", kind)

                    thinking.empty()

                    token = payload.get(
                    "token",
                    ""
                    )

                    print("token:", token)

                    final += token


                    # remove completed think blocks

                    clean = re.sub(

                    r"<think>.*?</think>",

                    "",

                    final,

                    flags=re.DOTALL

                    )


                    # remove unfinished streamed think block

                    clean = re.sub(

                    r"<think>.*",

                    "",

                    clean,

                    flags=re.DOTALL

                    )


                    holder.markdown(
                    clean
                    )


                # -----------------
                # INTERRUPT
                # -----------------

                elif kind == "interrupt":

                    st.session_state.processing=False

                    st.session_state.loading=False

                    st.session_state.show_loading_message=False


                    intr = payload.get(
                    "data",
                    {}
                    )


                    print(
                    "RAW INTERRUPT:",
                    intr
                    )


                    # handle list

                    if isinstance(
                    intr,
                    list
                    ):

                        if len(intr):

                            intr = intr[0]


                    st.session_state.interrupt = intr

                    st.rerun()


                # -----------------
                # NODE UPDATES
                # -----------------

                elif kind == "update":

                    data = payload[
                    "data"
                    ]

                    print(
                    "UPDATE:",
                    data
                    )
                    hidden = ["resolver","intent","supervisor","save_history"]

                    skip = False

                    for node in hidden:
                        

                        if node in data:

                            skip = True

                            break


                    if skip:

                        continue


                    text = ""


                    if "response" in data:

                        text = data[
                        "response"
                        ].get(
                        "response",
                        ""
                        )


                    elif "tracking" in data:

                        text = data[
                        "tracking"
                        ].get(
                        "response",
                        ""
                        )


                    elif "order" in data:

                        text = data[
                        "order"
                        ].get(
                        "response",
                        ""
                        )


                    elif "escalation" in data:

                        text = data[
                        "escalation"
                        ].get(
                        "response",
                        ""
                        )


                    elif "followup" in data:

                        text = data[
                        "followup"
                        ].get(
                        "response",
                        ""
                        )


                    if text:

                        thinking.empty()

                        final = text

                        holder.markdown(
                        final
                        )


        except ChunkedEncodingError:

            pass


    # SAVE MESSAGE

    if final:

        st.session_state.messages.append({

        "role":
        "assistant",

        "content":
        final

        })


    # RESET FLAGS

    st.session_state.processing=False

    st.session_state.loading=False

    st.session_state.show_loading_message=False


    st.rerun()
# --------------------------------
# HITL
# --------------------------------

if st.session_state.interrupt:

    intr = st.session_state.interrupt

    data = {}

    print(
    "RAW INTERRUPT:",
    intr
    )


    # object interrupt

    if hasattr(intr,"value"):

        data = intr.value


    # dict interrupt

    elif isinstance(
    intr,
    dict
    ):

        data = intr


    # string interrupt

    elif isinstance(intr,str):

        print(
        "RAW STRING:",
        intr
        )

        match = re.search(

        r"value=(\{.*?\})\s*,\s*id=",

        intr,

        flags=re.DOTALL

        )


        if match:

            raw = match.group(
            1
            )

            print(
            "MATCHED:",
            raw
            )

            try:

                data = ast.literal_eval(
                raw
                )

            except Exception as e:

                print(
                "PARSE ERROR:",
                e
                )


    # list fallback

    elif isinstance(intr,list):

        if len(intr):

            item = intr[0]

            print(
            "LIST ITEM:",
            item
            )


            # case:
            # [{"value": {...}}]

            if isinstance(
            item,
            dict
            ):

                if "value" in item:

                    data = item[
                    "value"
                    ]


            # case:
            # Interrupt object

            elif hasattr(
            item,
            "value"
            ):

                data = item.value


            # case:
            # string interrupt

            elif isinstance(
            item,
            str
            ):

                match = re.search(

                r"value=(\{.*?\})\s*,\s*id=",

                item,

                re.DOTALL

                )

                if match:

                    data = ast.literal_eval(

                    match.group(
                    1
                    )

                    )
    print(
    "Interrupt data:",
    data
    )


    question = str(
    data.get(
    "question",
    "Approval required"
    )
    )


    action = str(
    data.get(
    "action",
    ""
    )
    )


    options = data.get(
    "options",
    [
    "YES",
    "NO"
    ]
    )


    st.divider()

    st.markdown(
    "### 🔐 Human Approval Required"
    )

    st.markdown(
    question
    )


    def resume_flow(answer):

        st.session_state.processing=True

        st.session_state.loading=True

        st.session_state.show_loading_message=True


        response=requests.post(

        f"{API}/resume",

        json={

        "thread_id":
        st.session_state.thread_id,

        "answer":
        answer

        }

        )

        result=response.json()


        if "__interrupt__" in result:

            st.session_state.processing=False

            st.session_state.loading=False

            st.session_state.show_loading_message=False
            intr = result[
                "__interrupt__"
                ]

            st.session_state.interrupt=intr

            


            print(
                "RESUME INTERRUPT:",
                intr
                )

            st.rerun()


        st.session_state.interrupt=None

        st.session_state.processing=False

        st.session_state.loading=False

        st.session_state.show_loading_message=False

        text=result.get(
        "response"
        ) or ""


        if text:

            st.session_state.messages.append({

            "role":
            "assistant",

            "content":
            text

            })

        st.rerun()


         
    


    if action=="ADDRESS_CONFIRMATION":

        address=st.text_area(
        "New shipping address"
        )

        c1,c2=st.columns(2)

        with c1:

            if st.button(
            "Use Saved Address"
            ):

                resume_flow(
                "YES"
                )

        with c2:

            if st.button(
            "Use New Address"
            ):

                resume_flow(
                address
                )

    else:

        c1,c2=st.columns(2)

        with c1:

            if st.button(
            "YES"
            ):

                resume_flow(
                "YES"
                )

        with c2:

            if st.button(
            "NO"
            ):

                resume_flow(
                "NO"
                )

# --------------------------------
# LOADING
# --------------------------------

if st.session_state.processing:

    st.info(
    "⏳ Request in progress. Please wait..."
    )

elif st.session_state.loading:

    st.info(
    "Processing..."
    )