from database.mongo import orders

def get_order(order_id,customer_id):

    order = orders.find_one(
        {
            "_id":order_id,
            "customer_id":customer_id
        }
    )

    if not order:
        return None

    return order