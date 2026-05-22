from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["agentic_support"]

sessions_collection = db["sessions"]
messages_collection = db["messages"]

escalation_tickets_collection = db["escalation_tickets"]

followup_tickets_collection = db["followup_tickets"]

knowledge_collection = db["knowledge"]

history_collection = db["history"]


customers = db["customers"]
orders = db["orders"]
payments = db["payments"]
refunds = db["refunds"]
escalations = db["escalations"]

