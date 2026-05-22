import re

def clean_llm_output(
text:str
):

    if not text:

        return ""

    # remove think blocks

    text = re.sub(

        r"<think>.*?</think>",

        "",

        text,

        flags=re.DOTALL

    )

    # remove markdown

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    return text.strip()