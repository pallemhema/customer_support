import re

def extract_order_id(
    text
):

    match = re.search(
        r'ord\d+',
        text.lower()
    )

    if match:

        return match.group()

    return None