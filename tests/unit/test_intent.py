import json
from types import SimpleNamespace
from workflows.intent import intent_node


class DummyMessage:
    def __init__(self, content):
        self.content = content


def make_result(content):
    return {"messages": [DummyMessage(content)]}


def test_intent_greeting(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"greeting_intent","priority":"LOW"}'))
    state = {"query": "Hello!"}
    result = intent_node(state)

    assert result["intent"] == "greeting_intent"
    assert result["priority"] == "LOW"
    assert state["intent"] == "greeting_intent"


def test_intent_tracking(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"track_order","priority":"LOW"}'))
    state = {"query": "Track my order ord001"}
    result = intent_node(state)

    assert result["intent"] == "track_order"
    assert state["priority"] == "LOW"


def test_intent_refund(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"refund_issue","priority":"HIGH"}'))
    state = {"query": "Refund failed"}
    result = intent_node(state)

    assert result["intent"] == "refund_issue"
    assert result["priority"] == "HIGH"


def test_intent_payment_issue(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"payment_issue","priority":"CRITICAL"}'))
    state = {"query": "Payment failed repeatedly"}
    result = intent_node(state)

    assert result["intent"] == "payment_issue"
    assert result["priority"] == "CRITICAL"


def test_intent_account_issue(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"account_issue","priority":"HIGH"}'))
    state = {"query": "My account is compromised"}
    result = intent_node(state)

    assert result["intent"] == "account_issue"
    assert result["priority"] == "HIGH"


def test_intent_create_order(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"create_order","priority":"LOW"}'))
    state = {"query": "I want to buy a laptop"}
    result = intent_node(state)

    assert result["intent"] == "create_order"


def test_intent_cancel_order(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"cancel_order","priority":"LOW"}'))
    state = {"query": "Cancel order ord002"}
    result = intent_node(state)

    assert result["intent"] == "cancel_order"


def test_intent_escalation_intent(monkeypatch):
    monkeypatch.setattr("workflows.intent.intent_agent.invoke", lambda payload: make_result('{"intent":"refund_issue","priority":"HIGH"}'))
    state = {"query": "Refund is missing"}
    result = intent_node(state)

    assert result["intent"] == "refund_issue"
    assert result["priority"] == "HIGH"
