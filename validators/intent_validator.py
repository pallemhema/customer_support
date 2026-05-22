def validate_intent(
        query:str,
        intent:str,
        priority:str
):

    query = query.lower().strip()

    intent = intent.lower().strip()

    priority = priority.upper().strip()


    # -------------------------
    # TRACKING OVERRIDE
    # -------------------------

    tracking_map = {

        "track ticket":
        "track_ticket",

        "ticket status":
        "track_ticket",

        "track complaint":
        "track_complaint",

        "complaint status":
        "track_complaint",

        "track order":
        "track_order",

        "order status":
        "track_order",
        "order details":"track_order",

        "refund status":
        "track_refund",

        "track refund":
        "track_refund",

        "chargeback status":
        "track_chargeback",

        "followup status":
        "track_followup"

    }

    for word, mapped in tracking_map.items():

        if word in query:

            return {

                "intent":
                mapped,

                "priority":
                "LOW"

            }


    # -------------------------
    # HARD SECURITY OVERRIDES
    # -------------------------

    security_words = [

        "account hacked",

        "unauthorized access",

        "account compromised",

        "someone changed my email",

        "fraud",

        "money deducted twice",

        "duplicate payment"

    ]

    if any(
        word in query
        for word in security_words
    ):

        return {

            "intent":
            "account_issue",

            "priority":
            "CRITICAL"

        }


    # -------------------------
    # VALID INTENTS
    # -------------------------

    allowed_intents = [

        "general_query",

        "payment_issue",

        "refund_issue",

        "login_issue",

        "subscription_issue",

        "delivery_issue",

        "technical_issue",

        "account_issue",

        "complaint",

        "feature_request",

        "track_ticket",

        "track_order",

        "track_complaint",

        "track_refund",

        "track_chargeback",

        "track_followup",

        "get_orders",
        "order_details",
        "greeting_intent",
        "customer_profile",
        "create_order",

    "cancel_order"


    ]

    if intent not in allowed_intents:

        intent = "general_query"


    # -------------------------
    # VALID PRIORITIES
    # -------------------------

    allowed_priority = [

        "LOW",

        "MEDIUM",

        "HIGH",

        "CRITICAL"

    ]

    if priority not in allowed_priority:

        priority = "LOW"


    return {

        "intent":
        intent,

        "priority":
        priority

    }