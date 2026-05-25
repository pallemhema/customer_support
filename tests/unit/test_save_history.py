from workflows.save_history import save_history
from types import SimpleNamespace


def test_save_history_skips_when_waiting_approval():
    state = {"thread_id": "thread1", "waiting_approval": True}
    result = save_history(state)
    assert result == {}


def test_save_history_skips_duplicate_resume(monkeypatch):
    state = {"thread_id": "thread2", "query": "Hello", "resume_execution": True}
    history = {"messages": [{"role": "user", "content": "Hello"}]}
    mock_collection = SimpleNamespace(find_one=lambda query: history, update_one=lambda *args, **kwargs: None)
    monkeypatch.setattr("workflows.save_history.history_collection", mock_collection)

    result = save_history(state)
    assert result == {}


def test_save_history_updates_history(monkeypatch):
    state = {
        "thread_id": "thread3",
        "query": "What is my order status?",
        "intent": "track_order",
        "route": "tracking",
        "customer_id": "cust001",
        "session_id": "sess1",
        "response": "Order ord001 is out for delivery.",
    }
    updated = {}

    def fake_update_one(filter_query, update, upsert=False):
        updated["filter"] = filter_query
        updated["update"] = update
        updated["upsert"] = upsert

    mock_collection = SimpleNamespace(find_one=lambda query: None, update_one=fake_update_one)
    monkeypatch.setattr("workflows.save_history.history_collection", mock_collection)

    result = save_history(state)
    assert result == {}
    assert updated["filter"]["thread_id"] == "thread3"
    assert updated["upsert"] is True
    assert any(item["role"] == "assistant" for item in updated["update"]["$push"]["messages"]["$each"])
