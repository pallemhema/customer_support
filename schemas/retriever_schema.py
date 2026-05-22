from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)

from typing import Optional, Literal


# -------------------------
# Retrieve Docs
# -------------------------

class RetrieveDocsInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    query:str = Field(
        ...,
        min_length=3,
        max_length=500,
        description=
        "Customer query"
    )

    k:int = Field(
        default=1,
        ge=1,
        le=5,
        description=
        "Number of documents"
    )



# -------------------------
# Ticket History
# -------------------------

class RetrieveTicketHistoryInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    intent:Optional[
        Literal[
            "refund_issue",
            "payment_issue",
            "login_issue",
            "technical_issue",
            "delivery_issue",
            "account_issue"
        ]
    ] = Field(
        default=None
    )

    priority:Optional[
        Literal[
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]
    ] = Field(
        default=None
    )



# -------------------------
# Chat History
# -------------------------

class RetrieveChatHistoryInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    session_id:str = Field(
        ...,
        min_length=3,
        max_length=100,
        description=
        "Conversation session id"
    )



# -------------------------
# Similar Issue Search
# -------------------------

class SimilarIssueSearchInput(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    query:str = Field(
        ...,
        min_length=3,
        max_length=500
    )

    k:int = Field(
        default=3,
        ge=1,
        le=5
    )