from workflows.followup import followup_node
from types import SimpleNamespace


def make_chunk(content):
    return SimpleNamespace(content=content)


def test_followup_generation(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Followup scheduled for tomorrow."), None)

    monkeypatch.setattr("workflows.followup.followup_agent.stream", fake_stream)
    state = {"query": "Any update?", "ticket_id": "T100", "response": "Escalation completed."}
    result = followup_node(state)

    assert result["followup"] == "Followup scheduled for tomorrow."
    assert "Escalation completed." in result["response"]


def test_followup_no_ticket():
    state = {"query": "Need followup", "response": "Escalation done."}
    result = followup_node(state)
    assert result["followup"] is None


def test_followup_response_merge(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Scheduled update call."), None)

    monkeypatch.setattr("workflows.followup.followup_agent.stream", fake_stream)
    state = {"query": "Please follow up", "ticket_id": "T200", "response": "Escalation sent."}
    result = followup_node(state)

    assert "Escalation sent." in result["response"]
    assert "Scheduled update call." in result["response"]
