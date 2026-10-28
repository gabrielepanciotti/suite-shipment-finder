"""iospedisco.it — WordPress front, ZK app behind. No price API: the prices page is HTML whose
analytics payload (`view_item_list`) carries every offer as structured JSON, so we read that."""

from __future__ import annotations

import re

import httpx

from ..models import Offer, QuoteRequest
from ._common import blocked_or_error, gross, make_client, pick_by_city
from .base import SourceError

SITE = "https://www.iospedisco.it"
APP = "https://pro.iospedisco.it/vw/spedisciAdesso.zul"

# The payload is JSON escaped inside a JS string, hence the optional backslashes.
_ITEM = re.compile(
    r'\\*"price\\*":\s*([\d.]+)\s*,\s*\\*"index\\*":\s*\d+\s*,\s*'
    r'\\*"item_name\\*":\s*\\*"([^"\\]*)\\*"\s*,\s*\\*"item_brand\\*":\s*\\*"([^"\\]*)\\*"'
)


def parse_offers(html: str, url: str = "") -> list[Offer]:
    """Prices are net of VAT on this site: normalise to gross so sources compare."""
    items = _ITEM.findall(html)
    if not items and "spedisciAdesso" not in html and "compara" not in html.lower():
        raise SourceError("changed", "neither offers nor the prices page were found")
    return [
        Offer(
            source="iospedisco",
            carrier=brand.strip().title(),
            service=name.strip().title(),
            price_eur=gross(float(price)),
            url=url or SITE + "/",
        )
        for price, name, brand in items
    ]


def _dim(v: float) -> str:
    return f"{v:g}"


class IoSpediscoSource:
    name = "iospedisco"

    async def _locality(self, client: httpx.AsyncClient, nonce: str, cap: str, city: str) -> dict:
        r = await client.get(
            f"{SITE}/wp-admin/admin-ajax.php",
            params={"action": "cf_search_city", "security": nonce, "state": "IT", "city": cap},
        )
        blocked_or_error(r, "cf_search_city")
        data = (r.json() or {}).get("data") or []
        data = [d for d in data if str(d.get("cap")) == cap]
        if not data:
            raise SourceError("empty", f"unknown postal code {cap}")
        return pick_by_city(data, city, "localita")

    async def quote(self, request: QuoteRequest) -> list[Offer]:
        async with make_client() as client:
            home = await client.get(SITE + "/")
            blocked_or_error(home, "home")
            m = re.search(r'data-security="([^"]+)"', home.text)
            if not m:
                raise SourceError("changed", "security nonce not found on the home page")
            nonce = m.group(1)
            a = await self._locality(client, nonce, request.sender.postal_code, request.sender.city)
            b = await self._locality(
                client, nonce, request.recipient.postal_code, request.recipient.city
            )

            p = request.parcel
            params: dict[str, str] = {"a": str(a["id"]), "b": str(b["id"]), "redirect": SITE}
            for i in range(p.count):
                params[f"c{i + 1}"] = (
                    f"{_dim(p.height_cm)};{_dim(p.width_cm)};{_dim(p.length_cm)};{_dim(p.weight_kg)}"
                )
            r = await client.get(APP, params=params)
            blocked_or_error(r, "spedisciAdesso")
            return parse_offers(r.text, url=str(r.url))
