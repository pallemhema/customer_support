import time


def tool_with_retry(
    func,
    *args,
    retries=3,
    delay=1,
    **kwargs
):
    """
    Retry normal tools
    DB
    API
    RAG
    Mongo
    """

    last_error = None

    for attempt in range(
        retries
    ):

        try:

            return func(
                *args,
                **kwargs
            )

        except Exception as e:

            # HITL must escape

            if "Interrupt(" in str(e):

                raise e

            last_error = e

            print(

f"""
Tool failed

Attempt:

{attempt+1}/{retries}

Error:

{e}
"""

            )

            time.sleep(
                delay
            )

    raise last_error



def tool_without_retry(
    func,
    *args,
    **kwargs
):
    """
    For interrupt tools
    Order
    Cancel
    Refund approval
    Account lock
    """

    return func(
        *args,
        **kwargs
    )