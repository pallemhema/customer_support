import re

def extract_order_id(
text
):

    matches = re.findall(

        r"\bord[a-zA-Z0-9]{4,}\b",

        str(text),

        re.IGNORECASE

    )

    if not matches:

        return None

    return max(
        matches,
        key=len
    )