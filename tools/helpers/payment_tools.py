from database.mongo import payments

from tools.tool_retry import (
    tool_with_retry
)

    
def get_payment(order_id:str,customer_id:str):
    try:
            
        if payments is None:
            return None

        payment = tool_with_retry(payments.find_one,{"_id":customer_id   })
        if not payment:
            return None
        return payment
    except Exception:
        return None
