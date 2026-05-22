from database.mongo import (
    customers
)
def get_profile(customer_id:str):

    """Get customer profile details."""

    profile = customers.find_one({"_id":customer_id   })

    return profile
