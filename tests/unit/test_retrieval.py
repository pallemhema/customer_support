from workflows.retriever import retrieval_node
from types import SimpleNamespace


class DummyMessage:
    def __init__(self, content):
        self.content = content


def make_result(messages):
    return {"messages": [DummyMessage(m) for m in messages]}


def test_retrieval_success(monkeypatch):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: make_result(["Relevant answer.\n", "Final doc content."]))
    state = {"query": "Where is ord001?", "resolved_query": "Where is ord001?", "intent": "track_order"}
    result = retrieval_node(state)
    assert result["retrieved_docs"] == "Final doc content."


def test_retrieval_empty(monkeypatch):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: make_result(["", "   "]))
    state = {"query": "What is your refund policy?", "resolved_query": "What is your refund policy?", "intent": "general_query"}
    result = retrieval_node(state)
    assert result["retrieved_docs"] == ""


def test_retrieval_multiple_documents(monkeypatch):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: make_result(["Doc1", "Doc2"]))
    state = {"query": "What happened to my order?", "resolved_query": "What happened to my order?", "intent": "track_order"}
    result = retrieval_node(state)
    assert result["retrieved_docs"] == "Doc2"


def test_retrieval_irrelevant_documents(monkeypatch):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: make_result(["OUT_OF_SCOPE"]))
    state = {"query": "How do I reset password?", "resolved_query": "How do I reset password?", "intent": "login_issue"}
    result = retrieval_node(state)
    assert result["retrieved_docs"] == "OUT_OF_SCOPE"
