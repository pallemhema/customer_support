from schemas.supervisor_state_schema import SupportState
from validators.intent_validator import validate_intent
def supervisor_node(
state:SupportState
):

    query = state[
        "query"
    ].lower()

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
    order_intents = [

    "create_order",

    "cancel_order"

    ]

    tracking_intents=[

        "track_ticket",

        "track_order",

        "track_complaint",

        "track_refund",

        "track_chargeback",

        "track_followup",

        "list_orders",
        "order_details",
        "customer_profile"

    ]


    tracking_keywords=[

        "list orders",

        "my orders",

        "show orders",

        "delivery status",

        "refund status",

        "track order",

        "order details"

    ]


    escalation_keywords=[

        "refund failed",

        "refund pending",

        "refund not received",

        "money deducted",

        "duplicate payment",

        "fraud",

        "hacked",

        "unauthorized",

        "payment failed",

        "account compromised"

    ]


    escalation_intents=[

        "refund_issue",

        "payment_issue",

        "security_issue",

        "account_recovery"

    ]

    if intent == "greeting_intent":
        return { "route":
            "response"
    }

    if intent in order_intents:

        return {

        "route":"order"

        }



    if intent in tracking_intents:

        return {

        "route":
        "tracking"

        }


    for word in tracking_keywords:

        if word in query:

            return {

            "route":
            "tracking"

            }


    if priority in [

        "HIGH",

        "CRITICAL"

    ]:

        return {

        "route":
        "escalation"

        }


    if intent in escalation_intents:

        return {

        "route":
        "escalation"

        }


    for word in escalation_keywords:

        if word in query:

            return {

            "route":
            "escalation"

            }


    return {

    "route":
    "normal"

    }

