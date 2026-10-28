"""Bits every site bot needs: a browser-ish HTTP client, VAT normalisation, locality matching."""

from __future__ import annotations

import httpx

from .base import SourceError

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154.0 Safari/537.36"
)
VAT_RATE = 1.22  # Italian VAT; Paccofacile quotes gross, the other two net
HTTP_TIMEOUT_S = 30.0


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept-Language": "it-IT,it;q=0.9"},
        follow_redirects=True,
        timeout=HTTP_TIMEOUT_S,
    )


def gross(net: float) -> float:
    return round(net * VAT_RATE, 2)


def parse_it_decimal(text: str) -> float:
    """'8,48' -> 8.48 ; '1.234,50' -> 1234.5"""
    return float(text.strip().replace(".", "").replace(",", "."))


def pick_by_city(candidates: list[dict], city: str, *name_keys: str) -> dict:
    """Prefer the locality whose name matches the requested city, else the first one."""
    wanted = city.strip().casefold()
    for cand in candidates:
        if any(str(cand.get(k, "")).strip().casefold() == wanted for k in name_keys):
            return cand
    return candidates[0]


def blocked_or_error(resp: httpx.Response, what: str) -> None:
    """Turn an unusable HTTP answer into a named SourceError."""
    if resp.status_code in (403, 429) or "captcha" in resp.text[:2000].lower():
        raise SourceError("blocked", f"{what}: HTTP {resp.status_code}")
    if resp.status_code >= 400:
        raise SourceError("error", f"{what}: HTTP {resp.status_code}")
