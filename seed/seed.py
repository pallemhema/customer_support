from database.mongo import *
from datetime import datetime
from database.mongo import *

print("Cleaning collections...")

customers.delete_many({})
orders.delete_many({})
payments.delete_many({})
refunds.delete_many({})

customers.insert_many([

{

"_id":"cust001",

"name":"Ravi Kumar",

"email":"ravi@gmail.com",

"phone":"+919876543210",

"address":{

"line1":"12 MG Road",

"city":"Hyderabad",

"state":"Telangana",

"country":"India",

"pincode":"500081"

},

"account_status":"ACTIVE",

"email_verified":True,

"created_at":datetime.utcnow(),

"last_login":datetime.utcnow()

},


{

"_id":"cust002",

"name":"Priya Sharma",

"email":"priya@gmail.com",

"phone":"+919812345678",

"address":{

"line1":"45 Banjara Hills",

"city":"Hyderabad",

"state":"Telangana",

"country":"India",

"pincode":"500034"

},

"account_status":"LOCKED",

"email_verified":True,

"created_at":datetime.utcnow(),

"last_login":datetime.utcnow()

}

])

orders.insert_many([

{

"_id":"ord001",

"customer_id":"cust001",

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

"delivery_status":"OUT_FOR_DELIVERY",

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

"_id":"ord002",

"customer_id":"cust002",

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


payments.insert_many([

{

"_id":"pay001",

"customer_id":"cust001",

"order_id":"ord001",

"amount":90000,

"currency":"INR",

"payment_method":"UPI",

"gateway":"Razorpay",

"transaction_id":"TXN001",

"payment_status":"SUCCESS",

"paid_at":datetime.utcnow(),

"fraud_flag":False,

"chargeback":False

},


{

"_id":"pay002",

"customer_id":"cust002",

"order_id":"ord002",

"amount":65000,

"currency":"INR",

"payment_method":"CARD",

"gateway":"Stripe",

"transaction_id":"TXN002",

"payment_status":"FAILED",

"error_code":"ERR-PAY-001",

"error_message":"Card declined",

"fraud_flag":False,

"chargeback":False,

"created_at":datetime.utcnow()

}

])

refunds.insert_many([

{

"_id":"ref001",

"customer_id":"cust001",

"order_id":"ord001",

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

},


{

"_id":"ref002",

"customer_id":"cust002",

"order_id":"ord002",

"payment_id":"pay002",

"return_completed":True,

"refund_requested":True,

"refund_status":"PENDING",

"refund_amount":65000,

"refund_days":4,

"reason":"Shipment damaged",

"requested_at":datetime.utcnow(),

"processed_at":None,

"finance_escalated":False

}

])