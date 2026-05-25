from workflows.supervisor import supervisor_node


def test_supervisor_routes_greeting_to_response():
    state = {"query": "Hi there", "intent": "greeting_intent", "priority": "LOW"}
    result = supervisor_node(state)
    assert result["route"] == "response"


def test_supervisor_routes_tracking_intent_to_tracking():
    state = {"query": "Where is my order?", "intent": "track_order", "priority": "LOW"}
    result = supervisor_node(state)
    assert result["route"] == "tracking"


def test_supervisor_routes_order_intent_to_order():
    state = {"query": "Buy a phone", "intent": "create_order", "priority": "LOW"}
    result = supervisor_node(state)
    assert result["route"] == "order"


def test_supervisor_routes_critical_priority_to_escalation():
    state = {"query": "Payment failed", "intent": "general_query", "priority": "CRITICAL"}
    result = supervisor_node(state)
    assert result["route"] == "escalation"


def test_supervisor_routes_refund_issue_to_escalation():
    state = {"query": "Refund not received", "intent": "refund_issue", "priority": "HIGH"}
    result = supervisor_node(state)
    assert result["route"] == "escalation"


def test_supervisor_routes_default_to_normal():
    state = {"query": "What is your return policy?", "intent": "general_query", "priority": "LOW"}
    result = supervisor_node(state)
    assert result["route"] == "normal"
