import time

from agents.llm import llm


def agent_with_retry(

    agent,

    payload,

    retries=3,

    delay=1

):

    last_error = None

    for attempt in range(
        retries
    ):

        try:

            return agent.invoke(
                payload
            )

        except Exception as e:

            print(e)

            text = str(
                e
            )

            # HITL

            if "Interrupt(" in text:

                raise e

            # fallback switch

            if (

                "429" in text

                or

                "rate_limit"
                in text.lower()

                or

                "tokens per day"
                in text.lower()

                or

                "tokens per minute"
                in text.lower()

            ):

                print(
                    "Switching model..."
                )

                llm.switch_model()

            last_error = e

            print(

f"""
Agent failed

Attempt:

{attempt+1}/{retries}

Error:

{text}
"""

            )

            time.sleep(
                delay
            )

    raise last_error



def stream_agent_with_retry(

    agent,

    payload,

    retries=3,

    delay=1,

    **kwargs

):

    last_error = None

    for attempt in range(
        retries
    ):

        try:

            for chunk in agent.stream(

                payload,

                **kwargs

            ):

                yield chunk

            return

        except Exception as e:

            print(e)

            text = str(
                e
            )

            if "Interrupt(" in text:

                raise e

            if (

                "429" in text

                or

                "rate_limit"
                in text.lower()

                or

                "tokens per day"
                in text.lower()

                or

                "tokens per minute"
                in text.lower()

            ):

                print(
                    "Switching model..."
                )

                llm.switch_model()

            last_error = e

            print(

f"""
Stream failed

Attempt:

{attempt+1}/{retries}

Error:

{text}
"""

            )

            time.sleep(
                delay
            )

    raise last_error