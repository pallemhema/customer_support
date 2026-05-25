from workflows.reponse import response_node
from types import SimpleNamespace


def make_chunk(content):
    return SimpleNamespace(content=content)


def test_response_greeting(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Hello! "), None)
        yield (make_chunk("Thanks for reaching out."), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)
    state = {"query": "Hi there", "intent": "greeting_intent"}
    result = response_node(state)

    assert "Hello!" in result["response"]
    assert result["response"].strip().endswith("Thanks for reaching out.")


def test_response_rag(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Here is the information from docs."), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)
    state = {"query": "What is the status?", "retrieved_docs": "Delivery is delayed."}
    result = response_node(state)

    assert "Here is the information from docs." in result["response"]


def test_response_escalation(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Escalation is in progress."), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)
    state = {"query": "Refund failed", "escalation_result": "Ticket created."}
    result = response_node(state)

    assert "Escalation is in progress." in result["response"]


def test_response_followup(monkeypatch):
    def fake_stream(payload, stream_mode=None):
        yield (make_chunk("Followup scheduled."), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)
    state = {"query": "Any update?", "followup": "Followup created."}
    result = response_node(state)

    assert "Followup scheduled." in result["response"]
