

from agents.intent_agent import (
    intent_agent
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

