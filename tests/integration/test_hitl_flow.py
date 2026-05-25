from tools.order_tools import create_order as create_order_tool
from tools.escalation.refund_escalation import handle_refund as handle_refund_tool
from types import SimpleNamespace


def test_hitl_order_confirmation(monkeypatch):
    monkeypatch.setattr("tools.order_tools.get_profile", lambda cid: {"address": {"line1": "12 MG Road", "city": "Hyderabad", "state": "Telangana", "country": "India", "pincode": "500081"}})
    monkeypatch.setattr("tools.order_tools.orders", SimpleNamespace(insert_one=lambda order: None))
    monkeypatch.setattr("tools.order_tools.interrupt", lambda payload: "YES")

    result = create_order_tool.func("cust003", [{"name": "AirPods", "quantity": 1}])
    assert result["status"] == "PLACED"


def test_hitl_refund_approval(monkeypatch):
    monkeypatch.setattr("tools.escalation.refund_escalation.get_refund", lambda order_id, customer_id: {"refund_amount": 1000, "refund_status": "FAILED"})
    monkeypatch.setattr("tools.escalation.refund_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "T500"})
    monkeypatch.setattr("tools.escalation.refund_escalation.request_hitl", lambda action, ticket_id, question: {"approved": False})

    result = handle_refund_tool.func("sess5", "cust005", "ord500", "refund_issue", "HIGH", "Refund failed")
    assert result["status"] == "CANCELLED"
