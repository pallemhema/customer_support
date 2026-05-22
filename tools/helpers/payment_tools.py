from database.mongo import payments

def get_payment(order_id,customer_id):

    return payments.find_one(
        {
            "order_id":order_id,
            "customer_id":customer_id
        }
    )


def payment_success(order_id):

    payment = get_payment(order_id)

    if not payment:
        return False

    return payment.get(
        "payment_status"
    ) == "SUCCESS"