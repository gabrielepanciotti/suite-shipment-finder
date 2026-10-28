"""Contract every shipping source implements. One file per site, nothing shared but this."""

from __future__ import annotations

from typing import Protocol

from ..models import Offer, QuoteRequest


class SourceError(Exception):
    """Raised by a source to report a *named* failure instead of returning [] silently."""

    def __init__(self, status: str, detail: str = "") -> None:
        super().__init__(f"{status}: {detail}")
        self.status = status
        self.detail = detail


class ShippingSource(Protocol):
    name: str

    async def quote(self, request: QuoteRequest) -> list[Offer]:
        """Return offers, or raise SourceError. Returning [] means 'no service on this route'."""
        ...
