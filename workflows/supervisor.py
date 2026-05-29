import time

from schemas.supervisor_state_schema import SupportState


def supervisor_node(
    state: SupportState
):

    start_time = time.time()
    print(
        "ENTER: supervisor_node"
    )

    try:
        query = state.get(
            "query",
            ""
        ).lower()

        intent = state.get(
            "intent",
            ""
        ).lower()

        priority = state.get(
            "priority",
            "LOW"
        ).upper()

        print(
            "SUPERVISOR NODE Execution"
        )

        # -------------------------
        # GREETING
        # -------------------------

        if intent == "greeting_intent":
            return {
                "route": "response"
            }

        # -------------------------
        # ORDER ROUTES
        # -------------------------

        order_intents = [
            "create_order",
            "cancel_order",
            "list_customer_orders",
            "order_purchase",
            "buy_product",
            "place_order"
        ]

        if intent in order_intents:
            return {
                "route": "order"
            }

        order_keywords = [
            "buy",
            "purchase",
            "place order",
            "create order",
            "cancel order",
            "my orders",
            "show orders",
            "list orders",
            "abort order",
            "checkout"
        ]

        if any(word in query for word in order_keywords):
            return {
                "route": "order"
            }

        # -------------------------
        # TRACKING ROUTES
        # -------------------------

        tracking_intents = [
            "track_ticket",
            "track_order",
            "track_complaint",
            "track_refund",
            "track_chargeback",
            "track_followup",
            "order_details",
            "customer_profile",
            "delivery_status",
            "refund_status"
        ]

        if intent in tracking_intents:
            return {
                "route": "tracking"
            }

        tracking_keywords = [
            "track order",
            "delivery status",
            "refund status",
            "where is my order",
            "order details",
            "track refund",
            "ticket status",
            "profile",
            "customer details"
        ]

        if any(word in query for word in tracking_keywords):
            return {
                "route": "tracking"
            }

        # -------------------------
        # ESCALATION
        # -------------------------

        escalation_intents = [
            "refund_issue",
            "payment_issue",
            "security_issue",
            "account_recovery",
            "account_issue"
        ]

        escalation_keywords = [
            "refund failed",
            "refund pending",
            "refund not received",
            "money deducted",
            "duplicate payment",
            "fraud",
            "payment failed",
            "unauthorized",
            "account hacked",
            "account compromised"
        ]

        if priority in ["HIGH", "CRITICAL"]:
            return {
                "route": "escalation"
            }

        if intent in escalation_intents:
            return {
                "route": "escalation"
            }

        if any(word in query for word in escalation_keywords):
            return {
                "route": "escalation"
            }

        # -------------------------
        # DEFAULT
        # -------------------------

        return {
            "route": "normal"
        }

    finally:
        elapsed = time.time() - start_time
        print(
            f"EXIT: supervisor_node elapsed={elapsed:.3f}s"
        )
