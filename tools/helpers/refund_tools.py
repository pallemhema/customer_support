from database.mongo import refunds
from tools.tool_retry import (
    tool_with_retry
)
  
def get_refund(order_id:str,customer_id:str):
    try:
            
        if refunds is None:
            print("no refunds table exists")
            return None

        refund = tool_with_retry(refunds.find_one,{"customer_id":customer_id,"order_id":order_id   })
        print("refund record:", refund)
        if not refund:
            print("no refund exist")
            return None
        return refund
    except Exception:
        print("exception occured")
        return None
