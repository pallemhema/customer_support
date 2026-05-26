from agents.intent_agent import (
    intent_agent
)

from validators.intent_validator import (
    validate_intent
)

from helpers.clean_text import (
    clean_llm_output
)

from agents.agent_retry import (
    agent_with_retry
)

import json
import re


def intent_node(
    state
):

    print(
        "Intent Node execution"
    )

    query = state.get(

        "resolved_query",

        state["query"]

    )

    try:

        result = agent_with_retry(

            intent_agent,

            {

                "messages":[

                    (

                        "user",

                        query

                    )

                ]

            }

        )

        messages = result.get(
            "messages",
            []
        )

        if not messages:

            raise Exception(
                "Empty agent output"
            )

        cleaned = clean_llm_output(

            messages[
                -1
            ].content

        )

        print(
            "output:",
            cleaned
        )

    except Exception as e:

        print(
            "Intent failed:",
            e
        )

        cleaned = """

{
    "intent":"complaint",
    "priority":"LOW"
}

"""

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

            try:

                data = json.loads(
                    match.group()
                )

            except Exception:

                data = {

                    "intent":
                    "complaint",

                    "priority":
                    "LOW"
                }

        else:

            data = {

                "intent":
                "complaint",

                "priority":
                "LOW"
            }

    validated = validate_intent(

        query=
        state[
            "query"
        ],

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

        "intent":

        validated[
            "intent"
        ],

        "priority":

        validated[
            "priority"
        ]
    }