from database.mongo import (
    customers
)


from tools.tool_retry import (
    tool_with_retry
)



    
def get_profile(customer_id:str):
    try:
            
        if customers is None:
            return None

        profile = tool_with_retry(customers.find_one,{"_id":customer_id   })
        if not profile:
            return None
        return profile
    except Exception:
        return None
    
