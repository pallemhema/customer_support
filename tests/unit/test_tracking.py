from workflows.tracking import tracking_node
from types import SimpleNamespace


def make_chunk(content):
    return SimpleNamespace(content=content)


def test_tracking_valid_order(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Order ord001 is OUT_FOR_DELIVERY."), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Track order ord001", "customer_id": "cust001"}
    result = tracking_node(state)

    assert result["order_id"] == "ord001"
    assert "OUT_FOR_DELIVERY" in result["response"]


def test_tracking_missing_order(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Order ord999 not found."), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Track order ord999", "customer_id": "cust001"}
    result = tracking_node(state)

    assert result["order_id"] == "ord999"
    assert "not found" in result["response"].lower()


def test_tracking_invalid_order(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Invalid order reference."), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Track order blah", "customer_id": "cust001"}
    result = tracking_node(state)

    assert result["order_id"] is None or "Invalid" in result["response"]


def test_tracking_refund_status(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Your refund for ord101 is FAILED."), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Refund status ord101", "customer_id": "cust001"}
    result = tracking_node(state)

    assert "FAILED" in result["response"]


def test_tracking_delivery_status(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Your order ord102 is OUT_FOR_DELIVERY."), None)

    monkeypatch.setattr("workflows.tracking.tracking_agent.stream", fake_stream)
    state = {"query": "Delivery status ord102", "customer_id": "cust001"}
    result = tracking_node(state)

    assert "OUT_FOR_DELIVERY" in result["response"]
