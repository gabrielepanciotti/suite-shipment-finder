import httpx
import pytest

from shipmentfinder_backend.app import build_app
from shipmentfinder_backend.models import Offer
from shipmentfinder_backend.sources.base import SourceError
from shipmentfinder_backend.sources.fake import FakeSource

BODY = {
    "sender": {"postal_code": "11111", "city": "Alpha"},
    "recipient": {"postal_code": "22222", "city": "Beta"},
    "parcel": {"length_cm": 30, "width_cm": 20, "height_cm": 15, "weight_kg": 2},
}


def _transport() -> httpx.ASGITransport:
    sources = [
        FakeSource("a", [Offer(source="a", carrier="X", price_eur=9.9)]),
        FakeSource("b", fail=SourceError("blocked", "captcha")),
    ]
    return httpx.ASGITransport(app=build_app(lambda: sources))


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=_transport(), base_url="http://testserver")


@pytest.mark.asyncio
async def test_quotes_returns_best_and_degradations():
    async with _client() as client:
        data = (await client.post("/api/quotes", json=BODY)).json()
    assert data["best"]["price_eur"] == 9.9
    assert data["degraded"] == ["b: blocked (captcha)"]


@pytest.mark.asyncio
async def test_quotes_rejects_bad_dimensions():
    bad = {**BODY, "parcel": {**BODY["parcel"], "weight_kg": 0}}
    async with _client() as client:
        response = await client.post("/api/quotes", json=bad)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sources_listed():
    async with _client() as client:
        response = await client.get("/api/sources")
    assert response.json() == {"sources": ["a", "b"]}
