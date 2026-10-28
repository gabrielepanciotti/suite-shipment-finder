"""Finder-family API additions keep the legacy surface compatible."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import httpx
import pytest

from shipmentfinder_backend.app import build_app
from shipmentfinder_backend.vista import DEFAULT_VISTA

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_validation_error_uses_standard_error_envelope() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=build_app()),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/api/quotes", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == {
        "code": "validation_error",
        "message": "I dati inviati non sono validi.",
        "field": "sender",
    }
    assert isinstance(body["detail"], list)


@pytest.mark.asyncio
async def test_vista_is_available_with_explicit_local_claims(monkeypatch) -> None:
    import shipmentfinder_backend.app as app_module

    with monkeypatch.context() as local_environment:
        local_environment.setenv("ALLOW_DEV_OWNER", "1")
        local_environment.setenv("LIFE_VISTA_DEFAULT_ROLE", "admin")
        app_module = importlib.reload(app_module)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/vista")

    importlib.reload(app_module)
    assert response.status_code == 200
    assert response.json()["ruolo"] == "admin"


def test_default_vista_matches_node_config() -> None:
    config = json.loads((ROOT / "node.config").read_text(encoding="utf-8"))

    assert DEFAULT_VISTA == config["vista"]
