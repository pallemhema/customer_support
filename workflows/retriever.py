

from schemas.sequential_state_schema import (
    SupportState
)


from agents.retrieval_agent import (
    retrieval_agent
)


from helpers.clean_text import clean_llm_output


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


