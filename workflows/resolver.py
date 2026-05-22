from schemas.supervisor_state_schema import (SupportState)
from agents.llm import get_llm
from helpers.clean_text import clean_llm_output
llm = get_llm()
import re

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
    )

    reference_words = [

        "above",

        "previous",

        "mentioned",

        "that",

        "same",

        "it"

    ]

    needs_resolution = any(

        word in query.lower()

        for word in reference_words

    )

    if not needs_resolution:

        return {

        "resolved_query":
        query

        }


    prompt = f"""

You are a query reference resolver.

Task:

Use chat history only to replace references.

DO NOT change intent.

DO NOT change issue type.

DO NOT rewrite meaning.

DO NOT convert:

delivery -> refund

refund -> delivery

payment -> account

tracking -> refund

Keep the original customer intention exactly the same.

Only replace references like:

above order

previous order

that order

same order

it

mentioned order

Chat history:

{history}

Current customer query:

{query}

Examples:

History:

delivery status of ord001

Query:

delivery status of above order

Output:

delivery status of ord001


History:

refund status of ord001

Query:

refund status of previous order

Output:

refund status of ord001


History:

payment issue ord002

Query:

what happened to that payment

Output:

what happened to payment issue ord002


Return ONLY resolved query.

No explanation.

No reasoning.

No markdown.

"""

    output = llm.invoke(
    prompt
    )

    
    resolved = clean_llm_output(output.content.strip())

    print(
    "Resolved:",
    resolved
    )

    return {

    "resolved_query":
    resolved

    }