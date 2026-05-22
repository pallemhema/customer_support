from langchain_core.tools import tool
from langgraph.types import interrupt



from datetime import datetime
import uuid

from tools.helpers.get_order import get_order

@tool
def create_order(
customer_id:str,
items:list
):

    """
    Create order.

    items example:

    [

    {
    "name":"iPhone 15",
    "quantity":2
    },

    {
    "name":"AirPods",
    "quantity":1
    }

    ]
    """

    if not items:

        return {

        "status":
        "FAILED",

        "response":
        "No products found"

        }

    processed=[]

    total_items = 0

    for item in items:

        qty = item.get(
        "quantity",
        1
        )

        processed.append({

        "name":
        item["name"],

        "quantity":
        qty

        })

        total_items += qty

    order_id = (

    "ord"

    +

    uuid.uuid4().hex[
        :6
    ]

    )

    order = {

    "order_id":
    order_id,

    "customer_id":
    customer_id,

    "items":
    processed,

    "status":
    "PLACED",

    "created_at":
    datetime.utcnow()

    }

    orders.insert_one(
    order
    )

    return {

    "order_id":
    order_id,

    "status":
    "PLACED",

    "items":
    processed,

    "response":

f"""
Order created successfully.

Order ID:

{order_id}

Items:

{processed}

Total Items:

{total_items}

Status:

PLACED

"""

    }







@tool
def cancel_order(
    customer_id:str,
order_id:str
):

    """
    Cancel order.

    Allowed:

    PLACED

    PROCESSING

    Rejected:

    SHIPPED

    OUT_FOR_DELIVERY

    DELIVERED
    """

    order = get_order(
    order_id,customer_id)

    if not order:

        return {

        "status":
        "NOT_FOUND",

        "response":
        f"Order {order_id} not found"

        }

    status = order.get(
        "status"
    )

    blocked = [

    "SHIPPED",

    "OUT_FOR_DELIVERY",

    "DELIVERED"

    ]

    if status in blocked:

        return {

        "status":
        "CANNOT_CANCEL",

        "response":

f"""
Order {order_id}
already shipped.

Current Status:

{status}

Cancellation unavailable.

"""

        }

    approval = interrupt(

    {

    "waiting_approval":
    True,

    "action":
    "CANCEL_ORDER",

    "order_id":
    order_id,

    "question":

f"""
Can I cancel
order {order_id}?

""",

    "options":[

    "YES",

    "NO"

    ]

    }

    )

    approved = (

    str(
    approval
    ).upper()

    ==

    "YES"

    )

    if not approved:

        return {

        "status":
        "REJECTED",

        "response":

f"""
Cancellation rejected
for order {order_id}

"""

        }

    orders.update_one(

    {

    "order_id":
    order_id

    },

    {

    "$set":{

    "status":
    "CANCELLED",

    "cancelled_at":
    datetime.utcnow()

    }

    }

    )

    return {

    "status":
    "CANCELLED",

    "order_id":
    order_id,

    "response":

f"""
Order {order_id}

cancelled successfully.

Status:

CANCELLED

"""

    }



@tool
def list_customer_orders(
customer_id:str
):

    """
    List customer orders
    """

    docs = list(

    orders.find(

    {

    "customer_id":
    customer_id

    },

    {

    "_id":0

    }

    )

    )

    if not docs:

        return {

        "status":
        "EMPTY",

        "response":
        "No orders found"

        }

    return {

    "count":
    len(
        docs
    ),

    "orders":
    docs

    }