import re

def clean_llm_output(
text:str
):

    if not text:

        return ""


    # remove completed think block

    text = re.sub(

    r"<think>.*?</think>",

    "",

    text,

    flags=re.DOTALL

    )


    # remove unfinished streaming think block

    text = re.sub(

    r"<think>.*",

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