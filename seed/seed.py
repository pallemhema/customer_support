from database.mongo import customers
from datetime import datetime

customers.insert_many([
{
"_id":"cust001",
"name":"Ravi Kumar",
"email":"ravi@example.com",
"email_verified":True,
"account_status":"ACTIVE",
"last_login":datetime.utcnow(),
"phone":"9876543210",

"address":{
"house_no":"12-45",
"street":"MG Road",
"area":"Ameerpet",
"city":"Hyderabad",
"state":"Telangana",
"country":"India",
"pincode":"500016"
}
},

{
"_id":"cust002",
"name":"Priya Sharma",
"email":"priya@example.com",
"email_verified":True,
"account_status":"ACTIVE",
"last_login":datetime.utcnow(),
"phone":"9876543211",

"address":{
"house_no":"8-102",
"street":"Ring Road",
"area":"Vijay Nagar",
"city":"Bengaluru",
"state":"Karnataka",
"country":"India",
"pincode":"560040"
}
},

{
"_id":"cust003",
"name":"Anil Reddy",
"email":"anil@example.com",
"email_verified":False,
"account_status":"ACTIVE",
"last_login":datetime.utcnow(),
"phone":"9876543212",

"address":{
"house_no":"5-78",
"street":"Temple Street",
"area":"Madhapur",
"city":"Hyderabad",
"state":"Telangana",
"country":"India",
"pincode":"500081"
}
}
])

print("Customers inserted")