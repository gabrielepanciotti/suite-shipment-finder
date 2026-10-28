"""Deterministic stand-in used by tests and by the UI in demo mode."""

from __future__ import annotations

import asyncio

from ..models import Offer, QuoteRequest
from .base import SourceError


class FakeSource:
    def __init__(
        self,
        name: str,
        offers: list[Offer] | None = None,
        fail: Exception | None = None,
        delay_s: float = 0.0,
    ) -> None:
        self.name = name
        self._offers = offers or []
        self._fail = fail
        self._delay_s = delay_s

    async def quote(self, request: QuoteRequest) -> list[Offer]:
        if self._delay_s:
            await asyncio.sleep(self._delay_s)
        if self._fail:
            raise self._fail
        return list(self._offers)


__all__ = ["FakeSource", "SourceError"]
