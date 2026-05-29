from langchain_core.tools import tool
from langgraph.types import interrupt

from database.mongo import orders

from tools.helpers.get_profile import (
    get_profile
)

from tools.helpers.get_order import (
    get_order
)

from tools.tool_retry import (
    tool_with_retry,
    tool_without_retry
)

from datetime import datetime
import uuid


@tool
def create_order(
    customer_id:str,
    items:list
):

    """
    Create customer order.

    Workflow:

    1. Validate products

    2. Load customer profile

    3. Ask order approval

    4. Ask address confirmation

    5. Create order

    Args:

        customer_id:

            Customer identifier

        items:

            Product list

            Example:

            [
                {
                    "name":"mouse",
                    "quantity":1
                }
            ]

    Returns:

        status

        order_id

        items

        address

    Uses HITL:

        ORDER_CONFIRMATION

        ADDRESS_CONFIRMATION

    Notes:

        No retry around interrupt.

        Retry only for DB operations.
    """

    return tool_without_retry(
        _create_order,
        customer_id,
        items
    )


def _create_order(
    customer_id,
    items
):

    if not items:

        return {

            "status":
            "FAILED",

            "response":
            "No products found"

        }

    customer = tool_with_retry(
        get_profile,
        customer_id
    )

    if not customer:

        return {

            "status":
            "CUSTOMER_NOT_FOUND",
            "response":
            "Customer not found"

        }

    processed = []

    total_items = 0

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

    confirm = interrupt(

        {

            "waiting_approval":
            True,

            "action":
            "ORDER_CONFIRMATION",

            "question":

f"""
Confirm order

Items:

{processed}

Total:

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
            "CANCELLED"

        }

    address_response = interrupt(

        {

            "waiting_address":
            True,

            "action":
            "ADDRESS_CONFIRMATION",

            "question":

f"""
Ship to:

{default_address}

YES

or send address
""",

            "options":[

                "YES",

                "ADDRESS"

            ]

        }

    )

    shipping_address = default_address

    if str(
        address_response
    ).upper() != "YES":

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

    order_id = (

        "ord"

        +

        uuid.uuid4().hex[:6]

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

        "shipping_address":
        shipping_address,

        "created_at":
        datetime.utcnow(),

        "updated_at":
        datetime.utcnow()

    }

    tool_with_retry(
        orders.insert_one,
        order
    )

    return {

        "status":
        "PLACED",

        "order_id":
        order_id,

        "items":
        processed,

        "shipping_address":
        shipping_address

    }


@tool
def cancel_order(
    customer_id:str,
    order_id:str
):

    """
    Cancel customer order.

    Workflow:

    1. Load order

    2. Validate state

    3. Ask verification

    4. Ask final approval

    5. Update order

    Uses HITL:

        VERIFY_CANCEL_ORDER

        FINAL_CANCEL
    """

    return tool_without_retry(
        _cancel_order,
        customer_id,
        order_id
    )


def _cancel_order(
    customer_id,
    order_id
):

    order = tool_with_retry(

        get_order,

        order_id,

        customer_id

    )

    if not order:

        return {

            "status":
            "NOT_FOUND",

            "response":

f"""
Order:

{order_id}

not found.
"""

        }

    delivery_status = order.get(

        "delivery_status",

        "PLACED"

    )

    # --------------------
    # ALREADY CANCELLED
    # --------------------

    if delivery_status == "CANCELLED":

        return {

            "status":
            "ALREADY_CANCELLED",

            "order_id":
            order_id,

            "response":

f"""
Order:

{order_id}

is already cancelled.

No further action needed.
"""

        }

    # --------------------
    # BLOCKED STATES
    # --------------------

    blocked = [

        "SHIPPED",

        "OUT_FOR_DELIVERY",

        "DELIVERED",

        "RETURNED",

    ]

    if delivery_status in blocked:

        return {

            "status":
            "CANNOT_CANCEL",

            "order_id":
            order_id,

            "response":

f"""
Order:

{order_id}

Current Status:

{delivery_status}

Cancellation unavailable.
"""

        }

    # --------------------
    # HITL
    # --------------------

    verify = interrupt(

        {

            "waiting_approval":
            True,

            "action":
            "VERIFY_CANCEL_ORDER",

            "question":

f"""
Cancel order:

{order_id}

Current Status:

{delivery_status}

Proceed?
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
Cancellation rejected.

Order:

{order_id}

remains active.
"""

        }

    tool_with_retry(

        orders.update_one,

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

    query={"customer_id":customer_id}

    docs=list(orders.find(query))



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

    "status":"SUCCESS",

    "count":len(docs),

    "orders":docs,

    "response":docs

    }
