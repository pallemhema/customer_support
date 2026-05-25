import os
import sys
from unittest.mock import MagicMock

# Ensure the project root is importable for tests under tests/.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Provide fake langchain dependencies before modules import them.
# This avoids creating real LLM instances during test collection.

fake_pymongo = MagicMock()
fake_pymongo.MongoClient = MagicMock()
sys.modules.setdefault("pymongo", fake_pymongo)

fake_langchain_groq = MagicMock()

class FakeChatGroq:
    def __init__(self, *args, **kwargs):
        self.invoke = MagicMock()
        self.stream = MagicMock()

fake_langchain_groq.ChatGroq = FakeChatGroq

fake_langchain_agents = MagicMock()

def fake_create_agent(*args, **kwargs):
    agent = MagicMock()
    agent.invoke = MagicMock()
    agent.stream = MagicMock()
    return agent

fake_langchain_agents.create_agent = fake_create_agent

sys.modules.setdefault("langchain_groq", fake_langchain_groq)
sys.modules.setdefault("langchain", MagicMock(agents=fake_langchain_agents))
sys.modules.setdefault("langchain.agents", fake_langchain_agents)
