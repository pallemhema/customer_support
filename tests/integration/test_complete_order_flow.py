from types import SimpleNamespace
from workflows.resolver import resolver_node
from workflows.intent import intent_node
from workflows.supervisor import supervisor_node
from workflows.order import order_node
from workflows.save_history import save_history
from tools.order_tools import create_order as create_order_tool


def test_complete_order_graph_flow(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: {"messages": [SimpleNamespace(content='{"intent":"create_order","priority":"LOW"}')]})

    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Order created successfully. Order ID: ord777"}), None)

    monkeypatch.setattr("workflows.order.order_agent.stream", fake_stream)
    monkeypatch.setattr("workflows.save_history.history_collection", type("C", (), {"find_one": lambda self, q: None, "update_one": lambda self, *args, **kwargs: None})())

    state = {"query": "Buy iPhone 15", "customer_id": "cust001", "session_id": "sess2", "thread_id": "thread2", "messages": []}
    state.update(resolver_node(state))
    state.update(intent_node(state))
    state.update(supervisor_node(state))
    assert state["route"] == "order"

    state.update(order_node(state))
    assert "Order created successfully" in state["response"]
    save_history_result = save_history(state)
    assert save_history_result == {}


def test_create_order_interrupt_flow(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_profile", lambda cid: {"address": {"line1": "12 MG Road", "city": "Hyderabad", "state": "Telangana", "country": "India", "pincode": "500081"}})
    monkeypatch.setattr("tools.order_tools.orders", SimpleNamespace(insert_one=lambda order: None))
    monkeypatch.setattr("tools.order_tools.interrupt", lambda payload: "YES")

    result = create_order_tool.func("cust001", [{"name": "AirPods", "quantity": 2}])
    assert result["status"] == "PLACED"
    assert result["order_id"].startswith("ord")
