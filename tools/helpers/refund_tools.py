from database.mongo import refunds

def get_refund(order_id,customer_id):

    return refunds.find_one(
        {
            "order_id":order_id,
            "customer_id":customer_id
        }
    )
