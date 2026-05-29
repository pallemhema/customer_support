import time

from schemas.sequential_state_schema import (
    SupportState
)

from agents.retrieval_agent import (
    retrieval_agent
)

from helpers.clean_text import (
    clean_llm_output
)

from agents.agent_retry import (
    agent_with_retry
)


def retrieval_node(
    state: SupportState
):

    start_time = time.time()
    print(
        "ENTER: retrieval_node"
    )

    print(
        "retrieval_node Node execution"
    )

    query = state.get(

        "resolved_query",

        state[
            "query"
        ]

    )

    final_output = ""

    try:

        result = agent_with_retry(

            retrieval_agent,

            {

                "messages":[

                    (

                        "user",

f"""
Customer Query:

{query}

Intent:

{state['intent']}

Retrieve information.

Return final response.
"""

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
                "No retrieval output"
            )

        for msg in reversed(
            messages
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

    except Exception as e:

        print(
            "Retrieval failed:",
            e
        )

        final_output = """

Knowledge retrieval unavailable.

Proceeding without documents.

"""

    finally:
        elapsed = time.time() - start_time
        print(
            f"EXIT: retrieval_node elapsed={elapsed:.3f}s"
        )

    if not final_output.strip():

        final_output = """

No relevant documents found.

"""

    return {

        "retrieved_docs":
        final_output
    }