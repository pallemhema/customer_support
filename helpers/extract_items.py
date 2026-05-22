import re

def extract_items(query):

    pattern = r'(\d+)?\s*([A-Za-z0-9\s]+?)(?:,|and|$)'

    matches = re.findall(
        pattern,
        query
    )

    items=[]

    for qty,name in matches:

        name=name.strip()

        if not name:
            continue

        quantity = int(
            qty
        ) if qty else 1

        items.append({

        "name":
        name,

        "quantity":
        quantity

        })

    return items