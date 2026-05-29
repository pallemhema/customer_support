import re

from helpers.extract_id import (
    extract_order_id
)

from schemas.supervisor_state_schema import (
    SupportState
)

from helpers.clean_text import (
    clean_llm_output
)

from agents.llm import llm


CONTINUATION_TERMS = [

    "it",
    "that",
    "same",
    "above",
    "previous",
    "mentioned",

    "shipping address",
    "delivery address",

    "track",

    "status",

    "details",

    "where is it",

    "show address",

    "what about",

    "when",

    "its"

]


def resolver_node(
state: SupportState
):

    print(
        "Resolver node execution"
    )

    query = state[
        "query"
    ]

    history = state.get(
        "messages",
        []
    )[-4:]

    state[
        "messages"
    ] = history

    history_text = str(
        history
    )

    history_order = (
        extract_order_id(
            history_text
        )
    )

    last_order_id = (

        state.get(
            "last_order_id"
        )

        or

        history_order

    )

    last_topic = state.get(
        "last_topic"
    )

    lower_query = query.lower()

    print(
        "History:",
        history
    )

    print(
        "Recovered order:",
        last_order_id
    )

    # explicit order id

    order_match = re.search(

        r"\bord[a-zA-Z0-9]+\b",

        query,

        re.IGNORECASE

    )

    if order_match:

        order_id = (
            order_match.group()
        )

        state[
            "last_order_id"
        ] = order_id

        return {

            "resolved_query":
            query,

            "last_order_id":
            order_id

        }

    continuation = any(

        term in lower_query

        for term in
        CONTINUATION_TERMS

    )

    # fast continuation path

    if continuation and last_order_id:

        resolved = f"""
    {query}

    for order {last_order_id}
    """.strip()

        print(
            "Resolved:",
            resolved
        )

        return {

            "resolved_query":
            resolved,

            "last_order_id":
            last_order_id

        }
    if not continuation:

        return {

            "resolved_query":
            query

        }

    # LLM fallback

    prompt = f"""

Resolve continuation.

History:

{history}

Memory:

order:
{last_order_id}

topic:
{last_topic}

Query:

{query}

Return complete query.

Keep intent.

Add missing order.

No explanation.

"""

    output = llm.invoke(
        prompt
    )

    resolved = clean_llm_output(
        output.content.strip()
    )

    recovered = extract_order_id(
        resolved
    )

    if recovered:

        state[
            "last_order_id"
        ] = recovered

    print(
        "Resolved:",
        resolved
    )

    return {

        "resolved_query":
        resolved,

        "last_order_id":
        recovered
        or
        last_order_id

    }