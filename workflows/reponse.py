


from agents.response_agent import response_agent
from helpers.clean_text import clean_llm_output
from agents.response_agent import response_agent
from helpers.clean_text import clean_llm_output

def response_node(
state
):

    print(
    "RESPONSE NODE EXECUTION"
    )

    text = ""

    if state.get(
    "intent"
    ) == "greeting_intent":

        text += f"""
Customer greeting detected

Customer message:

{state['query']}

Respond warmly.

Keep response short.
"""


    if state.get(
    "retrieved_docs"
    ):

        text += str(
        state[
        "retrieved_docs"
        ]
        )


    if state.get(
    "escalation_result"
    ):

        text += "\n"

        text += str(
        state[
        "escalation_result"
        ]
        )


    if state.get(
    "followup"
    ):

        text += "\n"

        text += str(
        state[
        "followup"
        ]
        )


    prompt = f"""

Customer Query:

{state['query']}

Context:

{text}

Generate response

"""


    response = ""

    for chunk,meta in response_agent.stream(

    {

    "messages":[

    (

    "user",

    prompt

    )

    ]

    },

    stream_mode="messages"

    ):

        token = getattr(

        chunk,

        "content",

        ""

        )


        if not token:

            continue


        print(
        "TOKEN:",
        token
        )


        response += token


    response = clean_llm_output(
    response
    )


    print(
    "FINAL:",
    response
    )

   

    return {

    "response":
    response,

    "messages":[

    (

    "user",

    state[
    "query"
    ]

    ),

    (

    "assistant",

    response

    )

    ]

    }
