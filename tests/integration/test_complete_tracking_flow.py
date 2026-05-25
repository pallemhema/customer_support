from types import SimpleNamespace
from workflows.resolver import resolver_node
from workflows.intent import intent_node
from workflows.supervisor import supervisor_node
from workflows.tracking import tracking_node
from workflows.save_history import save_history


def test_complete_tracking_flow(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: {"messages": [SimpleNamespace(content='{"intent":"track_order","priority":"LOW"}') ]})

    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Your order ord555 is OUT_FOR_DELIVERY."}), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    monkeypatch.setattr("workflows.save_history.history_collection", type("C", (), {"find_one": lambda self, q: None, "update_one": lambda self, *args, **kwargs: None})())

    state = {"query": "Track my order ord555", "customer_id": "cust001", "session_id": "sess1", "thread_id": "thread1", "messages": []}
    state.update(resolver_node(state))
    state.update(intent_node(state))
    state.update(supervisor_node(state))
    assert state["route"] == "tracking"

    state.update(tracking_node(state))
    assert "OUT_FOR_DELIVERY" in state["response"]

    history_result = save_history(state)
    assert history_result == {}
