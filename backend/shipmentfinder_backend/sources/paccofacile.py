"""paccofacile.it — Laravel app. CSRF token from the home page, then two AJAX calls, JSON out."""

from __future__ import annotations

import json
import re

import httpx

from ..models import Offer, QuoteRequest
from ._common import blocked_or_error, make_client, pick_by_city
from .base import SourceError

BASE = "https://www.paccofacile.it"
AJAX = {"X-Requested-With": "XMLHttpRequest"}


def parse_offers(payload: dict) -> list[Offer]:
    """`data.services_available[]` -> offers (prices are VAT-included on this site)."""
    header = payload.get("header") or {}
    if header.get("status") == "ERROR":
        msgs = json.dumps((header.get("notification") or {}).get("messages"), ensure_ascii=False)
        raise SourceError("error", f"the site rejected the request: {msgs[:300]}")
    try:
        services = payload["data"]["services_available"]
    except (KeyError, TypeError) as exc:
        raise SourceError("changed", "services_available missing from the answer") from exc
    offers: list[Offer] = []
    for s in services:
        if not s.get("available_for_private_individuals", 1):
            continue
        days = (s.get("delivery_date") or {}).get("delivery_days")
        days_i = int(days) if str(days or "").isdigit() else None
        offers.append(
            Offer(
                source="paccofacile",
                carrier=str(s["carrier"]).title(),
                service=str(s["name"]).title(),
                price_eur=float(s["price_total"]["amount"]),
                delivery_days_min=days_i,
                delivery_days_max=days_i,
                url=BASE + "/",
            )
        )
    return offers


def _city_of(loc: dict) -> str:
    try:
        return json.loads(loc.get("gls_informazioni") or "{}").get("Comune", "")
    except ValueError:
        return ""


class PaccofacileSource:
    name = "paccofacile"

    async def _locality(self, client: httpx.AsyncClient, cap: str, city: str) -> dict:
        r = await client.get(
            f"{BASE}/ajax/shipment/search_locality",
            params={"word": cap, "country_iso": "IT"},
            headers=AJAX,
        )
        blocked_or_error(r, "search_locality")
        found = [loc for loc in r.json() if str(loc.get("cap")) == cap]
        if not found:
            raise SourceError("empty", f"unknown postal code {cap}")
        for loc in found:
            loc["_comune"] = _city_of(loc)
        return pick_by_city(found, city, "_comune", "comune")

    @staticmethod
    def _place(prefix: str, loc: dict) -> dict[str, str]:
        return {
            f"shipment[{prefix}][iso_code]": "it",
            f"shipment[{prefix}][postal_code]": str(loc["cap"]),
            f"shipment[{prefix}][city]": str(loc["locality"]),
            f"shipment[{prefix}][StateOrProvinceCode]": str(loc["StateOrProvinceCode"]),
            f"shipment[{prefix}][country_name]": "Italia",
            f"shipment[{prefix}][latitude]": str(loc["latitude"]),
            f"shipment[{prefix}][longitude]": str(loc["longitude"]),
            f"shipment[{prefix}][capID]": str(loc["capID"]),
        }

    async def quote(self, request: QuoteRequest) -> list[Offer]:
        async with make_client() as client:
            home = await client.get(BASE + "/")
            blocked_or_error(home, "home")
            m = re.search(r'name="csrf-token"\s+content="([^"]+)"', home.text) or re.search(
                r'content="([^"]+)"\s+name="csrf-token"', home.text
            )
            if not m:
                raise SourceError("changed", "csrf token not found on the home page")
            token = m.group(1)

            origin = await self._locality(client, request.sender.postal_code, request.sender.city)
            dest = await self._locality(
                client, request.recipient.postal_code, request.recipient.city
            )

            p = request.parcel
            form: dict[str, str] = {
                "passoCorrente": "scelta_destinazione",
                "shipment[shipment_service][shipment_type]": "1",
                "shipment[shipment_service][package_content_type]": "GOODS",
                "shipment[shipment_id]": "0",
                "shipment[carrier_code]": "",
                "shipment[content_type]": "",
                "_token": token,
            }
            for i in range(p.count):
                pre = f"shipment[shipment_service][parcels][{i}]"
                form |= {
                    f"{pre}[shipment_type]": "1",
                    f"{pre}[weight]": f"{p.weight_kg:.2f}",
                    f"{pre}[dim1]": f"{p.length_cm:.2f}",
                    f"{pre}[dim2]": f"{p.width_cm:.2f}",
                    f"{pre}[dim3]": f"{p.height_cm:.2f}",
                    f"{pre}[index_row]": str(i),
                }
            form |= self._place("pickup", origin) | self._place("destination", dest)

            r = await client.post(
                f"{BASE}/ajax/shipment/validation",
                data=form,
                headers={**AJAX, "X-CSRF-TOKEN": token, "Referer": BASE + "/"},
            )
            blocked_or_error(r, "validation")
            try:
                return parse_offers(r.json())
            except ValueError as exc:
                raise SourceError("changed", "validation answer is not JSON") from exc
