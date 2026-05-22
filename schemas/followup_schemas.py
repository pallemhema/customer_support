from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)

from typing import Literal


# -------------------------
# Schedule Followup
# -------------------------

class ScheduleFollowupInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    ticket_id:str = Field(
        ...,
        min_length=3,
        max_length=100,
        description=
        "Support ticket id"
    )

    hours:int = Field(
        default=24,
        ge=1,
        le=720,
        description=
        "Hours until followup"
    )

    @field_validator(
        "ticket_id"
    )
    @classmethod
    def validate_ticket(
        cls,
        value
    ):
        value = value.strip()

        if not value:
            raise ValueError(
                "ticket id empty"
            )

        return value



# -------------------------
# Send Followup Message
# -------------------------

class SendFollowupMessageInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    session_id:str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    message:str = Field(
        ...,
        min_length=5,
        max_length=1000
    )

    @field_validator(
        "message"
    )
    @classmethod
    def clean_message(
        cls,
        value
    ):
        return value.strip()



# -------------------------
# Pending Tickets
# -------------------------

class CheckPendingTicketsInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    pass



# -------------------------
# Close Ticket
# -------------------------

class CloseTicketInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    ticket_id:str = Field(
        ...,
        min_length=3,
        max_length=100
    )

class TrackTicketInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    ticket_id:str = Field(
        ...,
        min_length=3,
        max_length=100
    )