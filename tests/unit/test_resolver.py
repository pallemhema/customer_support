from types import SimpleNamespace
from workflows.resolver import resolver_node


def make_mock_response(content):
    return SimpleNamespace(content=content)


def test_resolver_normal_query_does_not_call_llm(monkeypatch):
    mock_llm = SimpleNamespace(invoke=SimpleNamespace())
    called = False

    def fake_invoke(_):
        nonlocal called
        called = True
        return make_mock_response("should not be used")

    mock_llm.invoke = fake_invoke
    monkeypatch.setattr("workflows.resolver.llm", mock_llm)

    state = {"query": "What is your return policy?", "messages": []}
    result = resolver_node(state)

    assert result["resolved_query"] == state["query"]
    assert not called


def test_resolver_missing_history_returns_original_query(monkeypatch):
    state = {"query": "What about the previous order?", "messages": []}
    result = resolver_node(state)

    assert result["resolved_query"] == state["query"]


def test_resolver_previous_order_reference_uses_llm(monkeypatch):
    query = "What is the status of the previous order?"
    expected = "Order status of ord123"
    mock_llm = SimpleNamespace(invoke=lambda prompt: make_mock_response(expected))
    monkeypatch.setattr("workflows.resolver.llm", mock_llm)

    state = {"query": query, "messages": ["Order status of ord123"]}
    result = resolver_node(state)

    assert result["resolved_query"] == expected


def test_resolver_above_order_reference_uses_llm(monkeypatch):
    query = "Provide tracking for above order"
    expected = "Provide tracking for ord456"
    mock_llm = SimpleNamespace(invoke=lambda prompt: make_mock_response(expected))
    monkeypatch.setattr("workflows.resolver.llm", mock_llm)

    state = {"query": query, "messages": ["Track order ord456"]}
    result = resolver_node(state)

    assert expected in result["resolved_query"]


def test_resolver_remove_think_blocks(monkeypatch):
    query = "Show status of that order"
    mock_llm = SimpleNamespace(invoke=lambda prompt: make_mock_response("<think>thinking</think>Track ord789"))
    monkeypatch.setattr("workflows.resolver.llm", mock_llm)

    state = {"query": query, "messages": ["Track order ord789"]}
    result = resolver_node(state)

    assert "<think>" not in result["resolved_query"]
    assert "Track ord789" == result["resolved_query"]
