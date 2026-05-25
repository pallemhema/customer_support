import pytest
from tools.escalation.refund_escalation import handle_refund as handle_refund_tool
from tools.escalation.account_escalation import handle_account as handle_account_tool


def test_handle_refund_missing_order_id():
    result = handle_refund_tool.func("sess1", "cust1", None, "refund_issue", "HIGH", "Refund missing")
    assert result["status"] == "FAILED"
    assert "Order ID missing" in result["response"]


def test_handle_refund_no_refund_record(monkeypatch):
    monkeypatch.setattr("tools.escalation.refund_escalation.get_refund", lambda order_id, customer_id: None)
    result = handle_refund_tool.func("sess1", "cust1", "ord100", "refund_issue", "HIGH", "Refund missing")
    assert result["status"] == "REFUND_NOT_FOUND"


def test_handle_refund_ticket_creation_and_escalation(monkeypatch):
    refund_record = {"refund_amount": 1000, "refund_status": "FAILED"}
    monkeypatch.setattr("tools.escalation.refund_escalation.get_refund", lambda order_id, customer_id: refund_record)
    monkeypatch.setattr("tools.escalation.refund_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "T100"})
    monkeypatch.setattr("tools.escalation.refund_escalation.request_hitl", lambda action, ticket_id, question: {"approved": True})
    monkeypatch.setattr("tools.escalation.refund_escalation.escalate_to_human", lambda ticket_id, team: {"assigned_team": "Finance Team", "status": "ESCALATED"})

    result = handle_refund_tool.func("sess1", "cust1", "ord100", "refund_issue", "HIGH", "Refund failed")
    assert result["status"] == "ESCALATED"
    assert result["ticket_id"] == "T100"
    assert result["assigned_team"] == "Finance Team"


def test_handle_refund_cancelled_on_hitl(monkeypatch):
    refund_record = {"refund_amount": 1000, "refund_status": "FAILED"}
    monkeypatch.setattr("tools.escalation.refund_escalation.get_refund", lambda order_id, customer_id: refund_record)
    monkeypatch.setattr("tools.escalation.refund_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "T200"})
    monkeypatch.setattr("tools.escalation.refund_escalation.request_hitl", lambda action, ticket_id, question: {"approved": False})

    result = handle_refund_tool.func("sess1", "cust1", "ord101", "refund_issue", "HIGH", "Refund failed")
    assert result["status"] == "CANCELLED"


def test_handle_account_security_issue(monkeypatch):
    monkeypatch.setattr("tools.escalation.account_escalation.get_profile", lambda cid: {"account_status": "ACTIVE", "email_verified": True, "last_login": "2026-05-24"})
    monkeypatch.setattr("tools.escalation.account_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "A100"})
    monkeypatch.setattr("tools.escalation.account_escalation.request_hitl", lambda action, ticket_id, question: {"approved": True})
    monkeypatch.setattr("tools.escalation.account_escalation.escalate_to_human", lambda ticket_id, team: {"assigned_team": "Security Team", "status": "ESCALATED"})

    result = handle_account_tool.func("sess1", "cust1", "account_issue", "CRITICAL", "My account was hacked")
    assert result["status"] == "ESCALATED"
    assert result["assigned_team"] == "Security Team"


def test_handle_account_compromise_rejected(monkeypatch):
    monkeypatch.setattr("tools.escalation.account_escalation.get_profile", lambda cid: {"account_status": "ACTIVE", "email_verified": True, "last_login": "2026-05-24"})
    monkeypatch.setattr("tools.escalation.account_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "A200"})
    monkeypatch.setattr("tools.escalation.account_escalation.request_hitl", lambda action, ticket_id, question: {"approved": False})

    result = handle_account_tool.func("sess1", "cust1", "account_issue", "CRITICAL", "My account was hacked")
    assert result["status"] == "CANCELLED"
