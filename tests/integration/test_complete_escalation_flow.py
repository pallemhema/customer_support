from tools.escalation.refund_escalation import handle_refund as handle_refund_tool
from workflows.followup import followup_node
from workflows.save_history import save_history
from types import SimpleNamespace


def test_complete_escalation_flow(monkeypatch):
    monkeypatch.setattr("tools.escalation.refund_escalation.get_refund", lambda order_id, customer_id: {"refund_amount": 1000, "refund_status": "FAILED"})
    monkeypatch.setattr("tools.escalation.refund_escalation.create_ticket", lambda session_id, intent, priority, customer_id, query: {"ticket_id": "T123"})
    monkeypatch.setattr("tools.escalation.refund_escalation.request_hitl", lambda action, ticket_id, question: {"approved": True})
    monkeypatch.setattr("tools.escalation.refund_escalation.escalate_to_human", lambda ticket_id, team: {"assigned_team": "Finance Team", "status": "ESCALATED"})

    result = handle_refund_tool.func("sess3", "cust002", "ord900", "refund_issue", "HIGH", "Refund failed")
    assert result["status"] == "ESCALATED"
    assert result["ticket_id"] == "T123"

    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Followup scheduled for tomorrow."}), None)

    monkeypatch.setattr("workflows.followup.followup_agent.stream", fake_stream)
    followup_state = {"query": "Any update?", "ticket_id": result["ticket_id"], "response": result["response"]}
    followup_result = followup_node(followup_state)
    assert "Followup scheduled" in followup_result["followup"]

    save_history_result = save_history({"thread_id": "thread3", "query": "Refund failed", "intent": "refund_issue", "route": "escalation", "customer_id": "cust002", "session_id": "sess3", "response": followup_result["response"], "messages": []})
    assert save_history_result == {}
