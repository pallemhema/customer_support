from workflows.supervisor import supervisor_node


def test_supervisor_routing_all_routes():
    cases = [
        ({"query": "Hi", "intent": "greeting_intent", "priority": "LOW"}, "response"),
        ({"query": "Track my order", "intent": "track_order", "priority": "LOW"}, "tracking"),
        ({"query": "Buy a phone", "intent": "create_order", "priority": "LOW"}, "order"),
        ({"query": "Refund failed", "intent": "refund_issue", "priority": "LOW"}, "escalation"),
        ({"query": "Payment failed", "intent": "general_query", "priority": "CRITICAL"}, "escalation"),
        ({"query": "What is the return policy?", "intent": "general_query", "priority": "LOW"}, "normal"),
    ]

    for state, expected in cases:
        result = supervisor_node(state)
        assert result["route"] == expected
