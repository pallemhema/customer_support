from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ConfigurationError
)

from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = None
db = None

try:

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # test connection
    client.admin.command("ping")

    db = client["agentic_support"]

    sessions_collection = db["sessions"]
    messages_collection = db["messages"]

    escalation_tickets_collection = db[
        "escalation_tickets"
    ]

    followup_tickets_collection = db[
        "followup_tickets"
    ]

    knowledge_collection = db[
        "knowledge"
    ]

    history_collection = db[
        "history"
    ]

    customers = db["customers"]
    orders = db["orders"]
    payments = db["payments"]
    refunds = db["refunds"]
    escalations = db["escalations"]

    print(
        "MongoDB connected successfully"
    )

except (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ConfigurationError
) as e:

    print(
        f"Mongo connection failed: {e}"
    )

    sessions_collection = None
    messages_collection = None

    escalation_tickets_collection = None
    followup_tickets_collection = None

    knowledge_collection = None
    history_collection = None

    customers = None
    orders = None
    payments = None
    refunds = None
    escalations = None