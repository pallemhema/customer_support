import streamlit as st
import requests
import uuid
import time

API = "http://localhost:8000"

st.set_page_config(
    page_title="Customer Support",
    layout="wide"
)

# -------------------------
# SESSION STATE
# -------------------------

if "customer_id" not in st.session_state:
    st.session_state.customer_id = "cust001"

if "last_customer" not in st.session_state:
    st.session_state.last_customer = (
        st.session_state.customer_id
    )

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )

if "thread_id" not in st.session_state:

    st.session_state.thread_id = (

        f"{st.session_state.customer_id}_"

        f"{st.session_state.session_id}"

    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interrupt" not in st.session_state:
    st.session_state.interrupt = None


# -------------------------
# SIDEBAR
# -------------------------

with st.sidebar:

    st.title(
        "🛎 Customer Support"
    )

    customer = st.text_input(
        "Customer ID",
        st.session_state.customer_id
    )

    st.session_state.customer_id = customer

    # ---------------------
    # CUSTOMER SWITCH
    # ---------------------

    if customer != st.session_state.last_customer:

        st.session_state.last_customer = customer

        st.session_state.messages = []

        st.session_state.interrupt = None

        try:

            sessions = requests.get(
                f"{API}/sessions/{customer}"
            ).json()

        except:

            sessions = []

        if sessions:

            latest = sessions[0]

            st.session_state.session_id = (
                latest["session_id"]
            )

            st.session_state.thread_id = (
                latest["thread_id"]
            )

            history = requests.get(
f"{API}/history/{latest['thread_id']}"
            ).json()

            st.session_state.messages = (

                history.get(
                    "messages",
                    []
                )

            )

        else:

            sid = str(
                uuid.uuid4()
            )

            st.session_state.session_id = sid

            st.session_state.thread_id = (

                f"{customer}_{sid}"

            )

            st.session_state.messages = []

        st.rerun()

    # ---------------------
    # NEW CHAT
    # ---------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        sid = str(
            uuid.uuid4()
        )

        st.session_state.session_id = sid

        st.session_state.thread_id = (

            f"{customer}_{sid}"

        )

        st.session_state.messages = []

        st.session_state.interrupt = None

        st.rerun()

    st.divider()

    st.subheader(
        "💬 Sessions"
    )

    try:

        sessions = requests.get(
f"{API}/sessions/{customer}"
        ).json()

    except:

        sessions = []

    for s in sessions:

        label = s.get(
            "title",
            "New Chat"
        )

        if len(label) > 35:

            label = (
                label[:35]
                + "..."
            )

        if st.button(
            label,
            key=s[
                "thread_id"
            ],
            use_container_width=True
        ):

            history = requests.get(
f"{API}/history/{s['thread_id']}"
            ).json()

            st.session_state.thread_id = (
                s["thread_id"]
            )

            st.session_state.session_id = (
                s["session_id"]
            )

            st.session_state.messages = (

                history.get(
                    "messages",
                    []
                )

            )

            st.session_state.interrupt = None

            st.rerun()


# -------------------------
# CHAT AREA
# -------------------------

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


# -------------------------
# CHAT INPUT
# -------------------------

query = st.chat_input(
"Ask your issue..."
)

if query:

    user_msg = {

        "role":
        "user",

        "content":
        query

    }

    st.session_state.messages.append(
        user_msg
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )

    response_box = st.empty()

    try:

        result = requests.post(

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

    except Exception as e:

        st.error(
            str(e)
        )

        st.stop()

    # ---------------------
    # INTERRUPT
    # ---------------------

    if "__interrupt__" in result:

        st.session_state.interrupt = (

            result[
                "__interrupt__"
            ][0]

        )

        st.rerun()

    # ---------------------
    # NORMAL RESPONSE
    # ---------------------

    else:

        text = result.get(
            "response",
            "No response"
        )

        current = ""

        for ch in text:

            current += ch

            response_box.markdown(
                current
            )

            time.sleep(
                0.01
            )

        st.session_state.messages.append(

        {

        "role":
        "assistant",

        "content":
        text

        }

        )


# -------------------------
# HITL PANEL
# -------------------------

if st.session_state.interrupt:

    intr = st.session_state.interrupt

    data = intr.get(
        "value",
        {}
    )

    question = data.get(
        "question",
        "Approval needed"
    )

    st.divider()

    st.info(

f"""
🔐 Human Approval Required

{question}

Select action below
"""

    )

    col1,col2,col3 = st.columns(
        [1,1,5]
    )

    # ---------------------
    # YES
    # ---------------------

    with col1:

        if st.button(
            "✅ YES"
        ):

            result = requests.post(

f"{API}/resume",

json={

"thread_id":
st.session_state.thread_id,

"answer":
"YES"

}

            ).json()

            st.session_state.interrupt = None

            text = result.get(
                "response",
                "Approved"
            )

            placeholder = st.empty()

            current = ""

            for ch in text:

                current += ch

                placeholder.markdown(
                    current
                )

                time.sleep(
                    0.01
                )

            st.session_state.messages.append(

            {

            "role":
            "assistant",

            "content":
            text

            }

            )

            st.rerun()

    # ---------------------
    # NO
    # ---------------------

    with col2:

        if st.button(
            "❌ NO"
        ):

            result = requests.post(

f"{API}/resume",

json={

"thread_id":
st.session_state.thread_id,

"answer":
"NO"

}

            ).json()

            st.session_state.interrupt = None

            text = result.get(
                "response",
                "Rejected"
            )

            placeholder = st.empty()

            current = ""

            for ch in text:

                current += ch

                placeholder.markdown(
                    current
                )

                time.sleep(
                    0.01
                )

            st.session_state.messages.append(

            {

            "role":
            "assistant",

            "content":
            text

            }

            )

            st.rerun()