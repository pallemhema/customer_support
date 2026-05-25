from tools.order_tools import create_order as create_order_tool, cancel_order as cancel_order_tool
from types import SimpleNamespace


class DummyInterrupt:
    def __init__(self, responses):
        self.responses = responses
        self.calls = 0

    def __call__(self, payload):
        if self.calls < len(self.responses):
            value = self.responses[self.calls]
            self.calls += 1
            return value
        return self.responses[-1]


def test_create_order_no_items():
    result = create_order_tool.func("cust001", [])
    assert result["status"] == "FAILED"


def test_create_order_customer_not_found(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_profile", lambda customer_id: None)
    result = create_order_tool.func("cust001", [{"name": "iPhone", "quantity": 1}])
    assert result["status"] == "CUSTOMER_NOT_FOUND"


def test_create_order_success(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_profile", lambda customer_id: {"address": {"line1": "12 MG Road", "city": "Hyderabad", "state": "Telangana", "country": "India", "pincode": "500081"}})
    mock_orders = SimpleNamespace(insert_one=lambda order: None)
    monkeypatch.setattr("tools.order_tools.orders", mock_orders)
    monkeypatch.setattr("tools.order_tools.interrupt", DummyInterrupt(["YES", "YES"]))

    result = create_order_tool.func("cust001", [{"name": "iPhone 15", "quantity": 1}])
    assert result["status"] == "PLACED"
    assert "order_id" in result


def test_cancel_order_not_found(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_order", lambda order_id, customer_id: None)
    result = cancel_order_tool.func("cust001", "ord999")
    assert result["status"] == "NOT_FOUND"


def test_cancel_order_cannot_cancel_shipped(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_order", lambda order_id, customer_id: {"delivery_status": "SHIPPED", "items": []})
    result = cancel_order_tool.func("cust001", "ord001")
    assert result["status"] == "CANNOT_CANCEL"


def test_cancel_order_rejected_on_confirmation(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_order", lambda order_id, customer_id: {"delivery_status": "PLACED", "items": []})
    monkeypatch.setattr("tools.order_tools.interrupt", DummyInterrupt(["NO"]))
    result = cancel_order_tool.func("cust001", "ord001")
    assert result["status"] == "REJECTED"


def test_cancel_order_success(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_order", lambda order_id, customer_id: {"delivery_status": "PLACED", "items": []})
    mock_orders = SimpleNamespace(update_one=lambda *args, **kwargs: None)
    monkeypatch.setattr("tools.order_tools.orders", mock_orders)
    monkeypatch.setattr("tools.order_tools.interrupt", DummyInterrupt(["YES", "YES"]))

    result = cancel_order_tool.func("cust001", "ord002")
    assert result["status"] == "CANCELLED"
    assert "Order cancelled successfully" in result["response"]
