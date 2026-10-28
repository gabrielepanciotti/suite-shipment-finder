import asyncio

import pytest
from shipmentfinder_backend.comparison import compare, rank
from shipmentfinder_backend.models import Offer, Parcel, Party, QuoteRequest, SourceStatus
from shipmentfinder_backend.sources.base import SourceError
from shipmentfinder_backend.sources.fake import FakeSource


def _req() -> QuoteRequest:
    return QuoteRequest(
        sender=Party(postal_code="11111", city="Alpha"),
        recipient=Party(postal_code="22222", city="Beta"),
        parcel=Parcel(length_cm=10, width_cm=10, height_cm=10, weight_kg=1),
    )


def _offer(src: str, price: float, days: int | None = None) -> Offer:
    return Offer(source=src, carrier="c", price_eur=price, delivery_days_max=days)


def test_rank_cheapest_first_then_faster():
    out = rank([_offer("a", 9, 5), _offer("b", 7, 4), _offer("c", 7, 2), _offer("d", 7)])
    assert [o.source for o in out] == ["c", "b", "d", "a"]


def test_compare_merges_and_names_every_degradation():
    sources = [
        FakeSource("ok", [_offer("ok", 12)]),
        FakeSource("cheap", [_offer("cheap", 8)]),
        FakeSource("blocked", fail=SourceError("blocked", "captcha")),
        FakeSource("empty"),
        FakeSource("boom", fail=ValueError("x")),
    ]
    res = asyncio.run(compare(_req(), sources, timeout_s=2))
    assert res.best and res.best.source == "cheap"
    by = {o.source: o.status for o in res.outcomes}
    assert by["blocked"] is SourceStatus.BLOCKED
    assert by["empty"] is SourceStatus.EMPTY
    assert by["ok"] is SourceStatus.OK
    assert by["boom"] is SourceStatus.ERROR
    assert any(d.startswith("blocked: blocked (captcha)") for d in res.degraded)
    assert not any(d.startswith("empty") for d in res.degraded)


def test_timeout_is_a_named_degradation():
    res = asyncio.run(
        compare(_req(), [FakeSource("slow", [_offer("slow", 5)], delay_s=1)], timeout_s=0.05)
    )
    assert res.outcomes[0].status is SourceStatus.TIMEOUT
    assert res.best is None and res.degraded


def test_same_place_is_rejected():
    p = Party(postal_code="11111", city="Alpha")
    with pytest.raises(ValueError):
        QuoteRequest(
            sender=p, recipient=p, parcel=Parcel(length_cm=1, width_cm=1, height_cm=1, weight_kg=1)
        )
