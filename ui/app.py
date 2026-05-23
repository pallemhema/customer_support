# import streamlit as st
# import requests
# import uuid
# import time

# API = "http://localhost:8000"

# st.set_page_config(
# page_title="Customer Support",
# layout="wide"
# )

# # --------------------------------
# # SESSION STATE
# # --------------------------------

# defaults = {

# "customer_id":"cust001",

# "last_customer":"cust001",

# "session_id":str(
# uuid.uuid4()
# ),

# "messages":[],

# "interrupt":None,

# "loading":False,

# # NEW
# "processing":False,

# "show_loading_message":False

# }

# for k,v in defaults.items():

#     if k not in st.session_state:

#         st.session_state[k] = v


# if "thread_id" not in st.session_state:

#     st.session_state.thread_id = (

#     f"{st.session_state.customer_id}_"

#     f"{st.session_state.session_id}"

#     )


# # --------------------------------
# # STREAM TEXT
# # --------------------------------

# def stream_text(
# text,
# placeholder
# ):

#     if not text:

#         return

#     current=""

#     for ch in text:

#         current += ch

#         placeholder.markdown(
#         current
#         )

#         time.sleep(
#         0.01
#         )


# # --------------------------------
# # SIDEBAR
# # --------------------------------

# with st.sidebar:

#     st.title(
#     "🛎 Customer Support"
#     )

#     customer = st.text_input(
#     "Customer ID",
#     st.session_state.customer_id
#     )


#     if customer != st.session_state.last_customer:

#         st.session_state.last_customer = customer

#         st.session_state.customer_id = customer

#         st.session_state.messages=[]

#         st.session_state.interrupt=None

#         st.session_state.loading=False

#         try:

#             sessions = requests.get(
# f"{API}/sessions/{customer}"
#             ).json()

#         except:

#             sessions=[]

#         if sessions:

#             latest=sessions[0]

#             st.session_state.session_id=latest[
#             "session_id"
#             ]

#             st.session_state.thread_id=latest[
#             "thread_id"
#             ]

#             history=requests.get(
# f"{API}/history/{latest['thread_id']}"
#             ).json()

#             st.session_state.messages=(

#             history.get(
#             "messages",
#             []
#             )

#             )

#         else:

#             sid=str(
#             uuid.uuid4()
#             )

#             st.session_state.session_id=sid

#             st.session_state.thread_id=(

#             f"{customer}_{sid}"

#             )

#         st.rerun()


#     if st.button(
#     "➕ New Chat",
#     use_container_width=True
#     ):

#         sid=str(
#         uuid.uuid4()
#         )

#         st.session_state.session_id=sid

#         st.session_state.thread_id=(

#         f"{customer}_{sid}"

#         )

#         st.session_state.messages=[]

#         st.session_state.interrupt=None

#         st.session_state.loading=False

#         st.rerun()


#     st.divider()

#     st.subheader(
#     "💬 Sessions"
#     )

#     try:

#         sessions=requests.get(
# f"{API}/sessions/{customer}"
#         ).json()

#     except:

#         sessions=[]


#     for s in sessions:

#         label=s.get(
#         "title",
#         "New Chat"
#         )

#         if len(label)>35:

#             label=label[:35]+"..."

#         if st.button(
#         label,
#         key=s["thread_id"],
#         use_container_width=True
#         ):

#             history=requests.get(
# f"{API}/history/{s['thread_id']}"
#             ).json()

#             st.session_state.thread_id=s[
#             "thread_id"
#             ]

#             st.session_state.session_id=s[
#             "session_id"
#             ]

#             st.session_state.messages=(

#             history.get(
#             "messages",
#             []
#             )

#             )

#             st.session_state.interrupt=None

#             st.rerun()


# # --------------------------------
# # CHAT
# # --------------------------------

# st.title(
# "🤖 Customer Support Assistant"
# )

# for msg in st.session_state.messages:

#     with st.chat_message(
#     msg["role"]
#     ):

#         st.markdown(
#         msg["content"]
#         )
#     # --------------------------------
# # TEMP RESPONSE LOADER
# # --------------------------------

# if (

# st.session_state.show_loading_message

# and

# st.session_state.processing

# ):

#     with st.chat_message(
#     "assistant"
#     ):

#         holder = st.empty()

#         loading_frames = [

#         "⏳ Loading",

#         "⏳ Loading.",

#         "⏳ Loading..",

#         "⏳ Loading..."

#         ]

#         holder.markdown(
#         loading_frames[
#         int(
#         time.time()*2
#         ) % 4
#         ]
#         )


# # --------------------------------
# # INPUT LOCK
# # --------------------------------

# disabled=(

# st.session_state.processing

# or

# st.session_state.loading

# or

# st.session_state.interrupt
# is not None

# )

# placeholder=(

# "⏳ Processing request..."

# if disabled

# else

# "Ask something..."

# )

# query=st.chat_input(

# placeholder,

# disabled=disabled

# )




# # --------------------------------
# # SEND QUERY
# # --------------------------------
# if query:

#     # SHOW QUERY FIRST

#     st.session_state.messages.append({

#     "role":
#     "user",

#     "content":
#     query

#     })

#     # STORE FOR API CALL

#     st.session_state.pending_query = query

#     # LOCK INPUT

#     st.session_state.processing = True

#     st.session_state.loading = True

#     # SHOW TEMP LOADER

#     st.session_state.show_loading_message = True

#     st.rerun()

# # --------------------------------
# # PROCESS PENDING QUERY
# # --------------------------------

# if (

# st.session_state.processing

# and

# "pending_query"
# in st.session_state

# ):

#     query = st.session_state.pending_query

#     del st.session_state.pending_query


#     result = requests.post(

#     f"{API}/chat",

#     json={

#     "customer_id":
#     st.session_state.customer_id,

#     "session_id":
#     st.session_state.session_id,

#     "thread_id":
#     st.session_state.thread_id,

#     "query":
#     query

#     }

#     ).json()


#     st.session_state.loading=False


#     # INTERRUPT

#     if "__interrupt__" in result:

#         st.session_state.processing=False

#         st.session_state.interrupt=(

#         result[
#         "__interrupt__"
#         ][0]

#         )

#         st.rerun()


#     text=result.get(
#     "response"
#     ) or ""


#     if text:

#         st.session_state.messages.append({

#         "role":
#         "assistant",

#         "content":
#         text

#         })


#     st.session_state.processing=False

#     st.rerun()
# # --------------------------------
# # HITL
# # --------------------------------

# if st.session_state.interrupt:

#     intr = st.session_state.interrupt

#     try:

#         if hasattr(
#         intr,
#         "value"
#         ):

#             data = intr.value

#         elif isinstance(
#         intr,
#         dict
#         ):

#             data = intr.get(
#             "value",
#             intr
#             )

#         else:

#             data={}

#     except:

#         data={}


#     question=str(
#     data.get(
#     "question",
#     "Approval required"
#     )
#     )

#     action=str(
#     data.get(
#     "action",
#     ""
#     )
#     )

#     st.divider()

#     st.markdown(
#     "### 🔐 Human Approval Required"
#     )

#     if action:

#         st.caption(
#         f"Action: {action}"
#         )

#     st.markdown(
#     question
#     )
#     def resume_flow(answer):

#         st.session_state.processing=True

#         st.session_state.loading=True

#         response=requests.post(

#         f"{API}/resume",

#         json={

#         "thread_id":
#         st.session_state.thread_id,

#         "answer":
#         answer

#         }

#         )

#         result=response.json()

#         st.session_state.loading=False

#         print(
#         "Resume result:",
#         result
#         )


#         if "__interrupt__" in result:

#             st.session_state.processing=False
#             st.session_state.show_loading_message=False

#             st.session_state.interrupt=(

#             result[
#             "__interrupt__"
#             ][0]

#             )

#             return


#         st.session_state.interrupt=None

#         text=result.get(
#         "response"
#         ) or ""

#         if text:

#             st.session_state.show_loading_message=False

#             st.session_state.messages.append({

#             "role":"assistant",

#             "content":
#             text

#             })

#         st.session_state.processing=False




#     if action == "ADDRESS_CONFIRMATION":

#         address=st.text_area(
#         "New shipping address"
#         )

#         c1,c2=st.columns(2)

#         with c1:

#             if st.button(
#             "Use Saved Address"
#             ):

#                 resume_flow(
#                 "YES"
#                 )

#         with c2:

#             if st.button(
#             "Use New Address"
#             ):

#                 resume_flow(
#                 address
#                 )

#     else:

#         c1,c2=st.columns(2)

#         with c1:

#             if st.button(
#             "YES"
#             ):

#                 resume_flow(
#                 "YES"
#                 )

#         with c2:

#             if st.button(
#             "NO"
#             ):

#                 resume_flow(
#                 "NO"
#                 )
import streamlit as st
import requests
import uuid
import time

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
# STREAM RESPONSE
# --------------------------------

def stream_text(
text,
placeholder
):

    current=""

    for ch in text:

        current += ch

        placeholder.markdown(
        current
        )

        time.sleep(
        0.01
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
# THINKING MESSAGE
# --------------------------------

if (

st.session_state.show_loading_message

and

st.session_state.processing

):

    with st.chat_message(
    "assistant"
    ):

        holder=st.empty()

        frames=[

        "🤖 Thinking",

        "🤖 Thinking.",

        "🤖 Thinking..",

        "🤖 Thinking..."

        ]

        holder.markdown(

        frames[
        int(
        time.time()*2
        ) % len(frames)
        ]

        )

        with st.spinner(
        ""
        ):

            time.sleep(
            0.1
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

"🤖 Thinking..."

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

    query=st.session_state.pending_query

    del st.session_state.pending_query


    result=requests.post(

    f"{API}/chat",

    json={

    "customer_id":
    st.session_state.customer_id,

    "session_id":
    st.session_state.session_id,

    "thread_id":
    st.session_state.thread_id,

    "query":
    query

    }

    ).json()


    if "__interrupt__" in result:

        st.session_state.processing=False

        st.session_state.loading=False

        st.session_state.show_loading_message=False

        st.session_state.interrupt=(

        result[
        "__interrupt__"
        ][0]

        )

        st.rerun()


    text=result.get(
    "response"
    ) or ""

    st.session_state.show_loading_message=False

    st.session_state.loading=False

    st.session_state.processing=False


    if text:

        st.session_state.messages.append({

        "role":
        "assistant",

        "content":
        text

        })

    st.rerun()


# --------------------------------
# HITL
# --------------------------------

if st.session_state.interrupt:

    intr=st.session_state.interrupt


    if hasattr(
    intr,
    "value"
    ):

        data=intr.value

    elif isinstance(
    intr,
    dict
    ):

        data=intr.get(
        "value",
        intr
        )

    else:

        data={}


    question=str(
    data.get(
    "question",
    "Approval required"
    )
    )

    action=str(
    data.get(
    "action",
    ""
    )
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

            st.session_state.interrupt=(

            result[
            "__interrupt__"
            ][0]

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