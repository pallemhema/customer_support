from schemas.supervisor_state_schema import (SupportState)

from helpers.clean_text import clean_llm_output

from agents.llm import llm
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

    

    history = history[-4:]

    state["messages"] = history
    
    print("History: ", history)
    

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
    # reference exists but no history

    if needs_resolution and not history:

        print(
        "No history available"
        )

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

delivery status of ordxxx

Query:

delivery status of above order

Output:

delivery status of ordxxxx


History:

refund status of ordxxx

Query:

refund status of previous order

Output:

refund status of ordxxxx


History:

payment issue ordxxxxx

the order id there can be any number of digits followed by ord

Query:

what happened to that payment

Output:

what happened to payment issue ordxxxx


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