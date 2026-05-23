from langchain_core.tools import tool
from langgraph.types import interrupt
from database.mongo import orders
from tools.helpers.get_profile import get_profile
from datetime import datetime
import uuid

from tools.helpers.get_order import get_order

from database.mongo import (
orders,
customers
)

from datetime import datetime
import uuid



@tool
def create_order(
customer_id:str,
items:list
):

    """
    Create order workflow
    """

    if not items:

        return {

        "status":
        "FAILED",

        "response":
        "No products found"

        }


    customer = get_profile(
    customer_id
    )

    if not customer:

        return {

        "status":
        "CUSTOMER_NOT_FOUND",

        "response":
        "Customer profile unavailable"

        }


    processed=[]

    total_items=0

    for item in items:

        qty = item.get(
        "quantity",
        1
        )

        processed.append({

        "name":
        item["name"],

        "qty":
        qty,

        "price":
        item.get(
        "price",
        0
        )

        })

        total_items += qty


    default_address = customer.get(
    "address",
    {}
    )


    # ------------------
    # ORDER CONFIRM
    # ------------------

    confirm = interrupt(

    {

    "waiting_approval":
    True,

    "action":
    "ORDER_CONFIRMATION",

    "question":

f"""

Please confirm order details

Items:

{processed}

Total Items:

{total_items}

Proceed?

""",

    "options":[

    "YES",

    "NO"

    ]

    }

    )


    if str(
    confirm
    ).upper() != "YES":

        return {

        "status":
        "CANCELLED",

        "response":

"""
Order creation cancelled

"""

        }


    # ------------------
    # ADDRESS STEP
    # ------------------

    address_response = interrupt(

    {

    "action":
    "ADDRESS_CONFIRMATION",

    "waiting_address":
    True,

    "question":

f"""

Ship to:

{default_address}

Reply YES

to use saved address

OR

enter new address:

Example:

12 MG Road
Hyderabad
Telangana
India
500081

""",

    "options":[

    "YES",

    "ADDRESS"

    ]

    }

    )


    shipping_address = default_address


    # USE SAVED

    if str(
    address_response
    ).upper() == "YES":

        shipping_address = default_address


    # CUSTOM ADDRESS

    else:

        lines = str(
        address_response
        ).split(
        "\n"
        )

        shipping_address = {

        "line1":

        lines[0]

        if len(lines)>0

        else "",

        "city":

        lines[1]

        if len(lines)>1

        else "",

        "state":

        lines[2]

        if len(lines)>2

        else "",

        "country":

        lines[3]

        if len(lines)>3

        else "",

        "pincode":

        lines[4]

        if len(lines)>4

        else ""

        }


    # ------------------
    # CREATE ORDER
    # ------------------

    order_id = (

    "ord"

    +

    uuid.uuid4().hex[
    :6
    ]

    )


    order = {

    "_id":
    order_id,

    "order_id":
    order_id,

    "customer_id":
    customer_id,

    "items":
    processed,

    "total_items":
    total_items,

    "currency":
    "INR",

    "delivery_status":
    "PLACED",

    "tracking_status":
    "PENDING",

    "courier":
    None,

    "tracking_id":
    None,

    "shipping_address":
    shipping_address,

    "created_at":
    datetime.utcnow(),

    "updated_at":
    datetime.utcnow()

    }


    orders.insert_one(
    order
    )


    return {

    "status":
    "PLACED",

    "order_id":
    order_id,

    "shipping_address":
    shipping_address,

    "items":
    processed,

    "response":

f"""

Order created successfully

Order ID:

{order_id}

Items:

{processed}

Shipping Address:

{shipping_address}

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
    Cancel order workflow
    """

    order = get_order(
    order_id,
    customer_id
    )

    if not order:

        return {

        "status":
        "NOT_FOUND",

        "response":

f"""
Order {order_id}
not found

"""

        }

    delivery_status = order.get(
    "delivery_status",
    "PLACED"
    )

    blocked = [

    "SHIPPED",

    "OUT_FOR_DELIVERY",

    "DELIVERED"

    ]

    if delivery_status in blocked:

        return {

        "status":
        "CANNOT_CANCEL",

        "response":

f"""
Order:

{order_id}

Current Status:

{delivery_status}

Cancellation unavailable.

"""

        }

    items = order.get(
    "items",
    []
    )

    verify = interrupt(

    {

    "waiting_approval":
    True,

    "action":
    "VERIFY_CANCEL_ORDER",

    "order_id":
    order_id,

    "question":

f"""

Please verify order details

Order ID:

{order_id}

Items:

{items}

Delivery Status:

{delivery_status}

Proceed with cancellation?

""",

    "options":[

    "YES",

    "NO"

    ]

    }

    )

    if str(
    verify
    ).upper() != "YES":

        return {

        "status":
        "REJECTED",

        "response":

f"""
Cancellation stopped.

Order:

{order_id}

remains active.

"""

        }

    final_confirmation = interrupt(

    {

    "waiting_approval":
    True,

    "action":
    "FINAL_CANCEL",

    "order_id":
    order_id,

    "question":

f"""

Final confirmation

Cancel order:

{order_id}

Continue?

""",

    "options":[

    "YES",

    "NO"

    ]

    }

    )

    if str(
    final_confirmation
    ).upper() != "YES":

        return {

        "status":
        "REJECTED",

        "response":

f"""
Final cancellation rejected.

Order:

{order_id}

remains active.

"""

        }

    orders.update_one(

    {

    "order_id":
    order_id

    },

    {

    "$set":{

    "delivery_status":
    "CANCELLED",

    "tracking_status":
    "CANCELLED",

    "cancelled_at":
    datetime.utcnow(),

    "updated_at":
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

Order cancelled successfully.

Order ID:

{order_id}

Status:

CANCELLED

Tracking:

CANCELLED

"""

    }


@tool
def list_customer_orders(
customer_id:str,
status:str=None,
product:str=None
):
    """
    Retrieve customer orders with optional filtering.

    Supports:

    1. All orders

    2. Orders by status

    3. Orders by product

    Examples:

    Show my orders

    Get my cancelled orders

    List delivered orders

    Show placed orders

    Show shipped orders

    Get AirPods orders

    Get iPhone orders

    Args:

        customer_id (str):

            Customer identifier.

        status (str, optional):

            Filter orders by status.

            Examples:

            CANCELLED

            PLACED

            SHIPPED

            OUT_FOR_DELIVERY

            DELIVERED

        product (str, optional):

            Filter by product name.

            Examples:

            iPhone

            AirPods

            Charger

    Returns:

        dict:

            count:
            Number of matching orders

            orders:
            Matching order list

            status:
            EMPTY if no orders found

    Used By:

        Order Agent

    Notes:

        If status not provided:

        Return all customer orders.

        Product filtering is case insensitive.

        Status filtering supports:

        PLACED

        PROCESSING

        CANCELLED

        SHIPPED

        OUT_FOR_DELIVERY

        DELIVERED

    """

    query={

    "customer_id":
    customer_id

    }

    docs=list(

    orders.find(
    query,
    {"_id":0}
    )

    )


    if status:

        filtered=[]

        for d in docs:

            order_status=(

            d.get(
            "status"
            )

            or

            d.get(
            "delivery_status"
            )

            or ""

            ).upper()


            if status.upper() in order_status:

                filtered.append(
                d
                )

        docs=filtered


    if product:

        p=[]

        for d in docs:

            items=d.get(
            "items",
            []
            )

            for item in items:

                if product.lower() in item.get(
                "name",
                ""
                ).lower():

                    p.append(
                    d
                    )

                    break

        docs=p


    if not docs:

        return {

        "status":
        "EMPTY",

        "response":

f"""
No {status or ''}
orders found

"""

        }


    return {

    "count":
    len(docs),

    "orders":
    docs

    }