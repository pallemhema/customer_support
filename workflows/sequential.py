from langgraph.graph import (
    StateGraph,
    START,
    END
)

from schemas.sequential_state_schema import (
    SupportState
)

from agents.intent_agent import (
    intent_agent
)

from agents.retrieval_agent import (
    retrieval_agent
)


from agents.response_agent import (
    response_agent
)
from langgraph.checkpoint.memory import (
    MemorySaver
)

import json
from validators.intent_validator import (
    validate_intent
)

from helpers.clean_text import clean_llm_output
import json
import re


def intent_node(state):

    print(
        "Intent Node execution"
    )

    query = state.get(
        "resolved_query",
        state["query"]
        )

    result = intent_agent.invoke(
        {
            "messages":[
                (
                    "user",
                    query
                )
            ]
        }
    )



    cleaned = clean_llm_output(result["messages"][-1].content)
    print("output: ", cleaned)
    




    try:

        data = json.loads(
            cleaned
        )

    except Exception:

        print(
            "JSON failed. Using fallback"
        )


        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL
        )


        if match:

            data = json.loads(
                match.group()
            )

        else:

            data = {

                "intent":
                "complaint",

                "priority":
                "LOW"
            }


    validated = validate_intent(

        query=
        state["query"],

        intent=
        data.get(
            "intent",
            "complaint"
        ),

        priority=
        data.get(
            "priority",
            "LOW"
        )

    )


    print(
        "VALIDATED:",
        validated
    )


    state[
        "intent"
    ] = validated[
        "intent"
    ]


    state[
        "priority"
    ] = validated[
        "priority"
    ]

    return {
        "intent":validated["intent"],
        "priority" :validated["priority"]  
    }

def retrieval_node(state: SupportState):
    print("retrieval_node Node execution")
    query = state.get(
        "resolved_query",
        state["query"]
        )

    result = retrieval_agent.invoke(
    {
        "messages":[("user",f"""Customer Query:{query}Intent:{state['intent']}
Retrieve information.
Return final response.
"""
        )
        ]
    }
    )
    

    final_output = ""

    for msg in reversed(
        result["messages"]
    ):

        content = getattr(
            msg,
            "content",
            ""
        )

        if (
            isinstance(
                content,
                str
            )
            and
            content.strip()
        ):
            content = clean_llm_output(
            content
            )

            final_output = content

            break

    return {"retrieved_docs":final_output,}



def response_node(
state
):

    text = ""

    

    # greeting

    if state.get("intent") == "greeting_intent":

        text +="""
            Customer greeting detected.

            Customer message:

            {state['query']}

            Respond warmly.

            If customer introduced themselves:

            Hi my name is Hema

            acknowledge the introduction.

            Keep response short.

            """

                    

    if state.get("retrieved_docs"):
        text += str(state["retrieved_docs"])

    if state.get("escalation_result"):
        text += "\n"
        text += str(state["escalation_result"])

    if state.get("followup"):
        text += "\n"
        text += str(state["followup"])

    result = response_agent.invoke({
        "messages":[
            ("user",
            f"""Customer Query:{state['query']} Context:{text} Generate response to the customer."""
            )
        ]
    })


    output = clean_llm_output(
            result["messages"][-1].content
            )
    print("output from reponse:", output)

    return {

        "response":output,
        "messages":[
            ("user",state["query"]),
            ("assistant",output)
        ]
    }

memory = MemorySaver()
graph = StateGraph(SupportState)

graph.add_node("intent",intent_node)

graph.add_node("retrieval",retrieval_node)

graph.add_node("response",response_node)

graph.add_edge(START,"intent")

graph.add_edge("intent","retrieval")


graph.add_edge("retrieval","response")


graph.add_edge("response",END)

app = graph.compile(checkpointer=memory)