from database.mongo import orders

from tools.tool_retry import (
    tool_with_retry
)


def get_order(
    order_id,
    customer_id
):


    try:
        if orders is None:
            print("no orders table exists")
            return None

        order = tool_with_retry(orders.find_one,{"_id":order_id,"customer_id":customer_id})

        if not order:
            print("no order exists")
            return None
        return order

    except Exception:
        return None