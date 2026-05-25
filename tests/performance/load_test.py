import pytest
from types import SimpleNamespace
from workflows.resolver import resolver_node
from workflows.retriever import retrieval_node
from workflows.reponse import response_node
from workflows.tracking import tracking_node
from workflows.save_history import save_history

pytest.importorskip("pytest_benchmark")


def test_resolver_latency(benchmark):
    state = {"query": "What is my order status?", "messages": []}
    benchmark(resolver_node, state)


def test_retrieval_latency(monkeypatch, benchmark):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: {"messages": [SimpleNamespace(content="Relevant doc.")]})
    state = {"query": "What is the delivery status?", "resolved_query": "What is the delivery status?", "intent": "track_order"}
    benchmark(retrieval_node, state)


def test_response_latency(monkeypatch, benchmark):
    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Hello"}), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)
    state = {"query": "Hi", "retrieved_docs": "Delivery info."}
    benchmark(response_node, state)


def test_tracking_latency(monkeypatch, benchmark):
    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Tracking info"}), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Track ord001", "customer_id": "cust001"}
    benchmark(tracking_node, state)


def test_history_save_latency(monkeypatch, benchmark):
    monkeypatch.setattr("workflows.save_history.history_collection", type("C", (), {"find_one": lambda self, q: None, "update_one": lambda self, *args, **kwargs: None})())
    state = {"thread_id": "thread-ps", "query": "Hello", "intent": "general_query", "route": "normal", "customer_id": "cust001", "session_id": "sess1", "response": "Hi"}
    benchmark(save_history, state)
