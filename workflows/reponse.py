

from agents.response_agent import (
    response_agent
)


from helpers.clean_text import clean_llm_output

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
