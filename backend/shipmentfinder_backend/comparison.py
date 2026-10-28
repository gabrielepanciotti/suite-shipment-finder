"""Fan the request out to every source, isolate failures, merge and rank."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence

from .models import Comparison, Offer, QuoteRequest, SourceOutcome, SourceStatus
from .sources.base import ShippingSource, SourceError

DEFAULT_TIMEOUT_S = 90.0


async def _run_one(
    source: ShippingSource, request: QuoteRequest, timeout_s: float
) -> SourceOutcome:
    started = time.monotonic()
    try:
        offers = await asyncio.wait_for(source.quote(request), timeout=timeout_s)
    except TimeoutError:
        return SourceOutcome(
            source=source.name,
            status=SourceStatus.TIMEOUT,
            detail=f"no answer in {timeout_s:.0f}s",
            elapsed_s=time.monotonic() - started,
        )
    except SourceError as exc:
        try:
            status = SourceStatus(exc.status)
        except ValueError:
            status = SourceStatus.ERROR
        return SourceOutcome(
            source=source.name,
            status=status,
            detail=exc.detail,
            elapsed_s=time.monotonic() - started,
        )
    except Exception as exc:  # a broken bot must never take the comparison down
        return SourceOutcome(
            source=source.name,
            status=SourceStatus.ERROR,
            detail=f"{type(exc).__name__}: {exc}",
            elapsed_s=time.monotonic() - started,
        )
    status = SourceStatus.OK if offers else SourceStatus.EMPTY
    return SourceOutcome(
        source=source.name, status=status, offers=offers, elapsed_s=time.monotonic() - started
    )


def rank(offers: Sequence[Offer]) -> list[Offer]:
    """Cheapest first; ties go to the faster service, unknown speed last."""
    return sorted(
        offers,
        key=lambda o: (o.price_eur, o.delivery_days_max if o.delivery_days_max is not None else 99),
    )


async def compare(
    request: QuoteRequest, sources: Sequence[ShippingSource], timeout_s: float = DEFAULT_TIMEOUT_S
) -> Comparison:
    outcomes = await asyncio.gather(*(_run_one(s, request, timeout_s) for s in sources))
    merged = rank([o for out in outcomes for o in out.offers])
    degraded = [
        f"{o.source}: {o.status.value}" + (f" ({o.detail})" if o.detail else "")
        for o in outcomes
        if o.status not in (SourceStatus.OK, SourceStatus.EMPTY)
    ]
    return Comparison(
        request=request,
        offers=merged,
        outcomes=list(outcomes),
        best=merged[0] if merged else None,
        degraded=degraded,
    )
