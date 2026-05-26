from database.mongo import refunds
from tools.tool_retry import (
    tool_with_retry
)
  
def get_refund(order_id:str,customer_id:str):
    try:
            
        if refunds is None:
            return None

        refund = tool_with_retry(refunds.find_one,{"_id":customer_id   })
        if not refund:
            return None
        return refund
    except Exception:
        return None
