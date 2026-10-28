"""The one type that crosses the whole pipeline: request in, offers out."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Party(BaseModel):
    """One end of the shipment. Quote forms only need where, not who."""

    postal_code: str = Field(min_length=3, max_length=10)
    city: str = Field(min_length=1)
    country: str = Field(default="IT", min_length=2, max_length=2)


class Parcel(BaseModel):
    length_cm: float = Field(gt=0)
    width_cm: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    count: int = Field(default=1, ge=1, le=20)


class QuoteRequest(BaseModel):
    sender: Party
    recipient: Party
    parcel: Parcel

    @model_validator(mode="after")
    def _distinct_ends(self) -> QuoteRequest:
        if self.sender == self.recipient:
            raise ValueError("sender and recipient are the same place")
        return self


class Offer(BaseModel):
    source: str
    carrier: str
    service: str = ""
    price_eur: float = Field(ge=0)
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None
    url: str = ""


class SourceStatus(StrEnum):
    OK = "ok"
    EMPTY = "empty"  # the site answered and has no service for this route
    BLOCKED = "blocked"  # captcha / anti-bot / 403
    CHANGED = "changed"  # the page no longer looks the way the bot expects
    TIMEOUT = "timeout"
    ERROR = "error"


class SourceOutcome(BaseModel):
    """Every source reports, even when it fails: an empty list must not look healthy."""

    source: str
    status: SourceStatus
    detail: str = ""
    offers: list[Offer] = []
    elapsed_s: float = 0.0


class Comparison(BaseModel):
    request: QuoteRequest
    offers: list[Offer]  # merged, cheapest first
    outcomes: list[SourceOutcome]
    best: Offer | None = None
    degraded: list[str] = []  # sources that did not contribute, with the reason
