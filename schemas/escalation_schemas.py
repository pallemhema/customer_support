from pydantic import (
    BaseModel,
    Field
)

from typing import Literal

from pydantic import (
    BaseModel,
    Field
)

from typing import Literal


# -------------------------
# Create Ticket
# -------------------------

from pydantic import BaseModel


class CreateTicketInput(
BaseModel
):

    session_id:str

    intent:str

    priority:str

    customer_id:str
    query:str


# -------------------------
# HITL Request
# -------------------------


class RequestHITLInput(
    BaseModel
):

    action:str

    ticket_id:str

    question:str


# -------------------------
# Escalation
# -------------------------

class EscalateToHumanInput(BaseModel):
    """
    Escalation input schema.
    """

    ticket_id:str = Field(
        ...,
        description="Ticket id"
    )

    team:str = Field(
        default="Support Team A",
        description="Target support team"
    )


# -------------------------
# Refund Request
# -------------------------

class CreateActionRequestInput(BaseModel):
    """
    Refund creation schema.
    """

    ticket_id:str = Field(
        ...,
        description="Ticket id"
    )
    action_type:str
    details:str

