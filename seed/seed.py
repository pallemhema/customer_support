from database.mongo import *
from datetime import datetime
from database.mongo import *

print("Cleaning collections...")

customers.delete_many({})
orders.delete_many({})
payments.delete_many({})
refunds.delete_many({})

orders.insert_many([

{

"_id":"ord0003",

"customer_id":"cust003",

"items":[

{

"product_id":"p001",

"name":"iPhone 15",

"qty":1,

"price":75000

},

{

"product_id":"p002",

"name":"AirPods",

"qty":1,

"price":15000

}

],

"total_amount":90000,

"currency":"INR",

"payment_id":"pay001",

"delivery_status":"RETURNED",

"tracking_status":"IN_TRANSIT",

"courier":"BlueDart",

"tracking_id":"TRK001",

"shipping_address":{

"city":"Hyderabad",

"state":"Telangana",

"country":"India"

},

"expected_delivery":"2026-05-22",

"delivered_on":None,

"created_at":datetime.utcnow(),

"updated_at":datetime.utcnow()

},


{

"_id":"ord0004",

"customer_id":"cust003",

"items":[

{

"product_id":"p003",

"name":"Laptop",

"qty":1,

"price":65000

}

],

"total_amount":65000,

"currency":"INR",

"payment_id":"pay002",

"delivery_status":"DELAYED",

"tracking_status":"EXCEPTION",

"courier":"Delhivery",

"tracking_id":"TRK002",

"expected_delivery":"2026-05-18",

"delay_reason":"Courier delay",

"created_at":datetime.utcnow(),

"updated_at":datetime.utcnow()

}

])



refunds.insert_many([

{

"_id":"ref0003",

"customer_id":"cust003",

"order_id":"ord0003",

"payment_id":"pay001",

"return_completed":True,

"refund_requested":True,

"refund_status":"FAILED",

"refund_amount":15000,

"refund_days":9,

"reason":"Product returned",

"requested_at":datetime.utcnow(),

"processed_at":None,

"finance_escalated":True

}
])