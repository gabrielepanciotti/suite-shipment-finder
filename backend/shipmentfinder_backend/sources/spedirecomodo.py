"""spedirecomodo.it — ASP.NET MVC. Anti-forgery token via JSON, one form POST, HTML out."""

from __future__ import annotations

import math
import re
from html import unescape

import httpx

from ..models import Offer, QuoteRequest
from ._common import blocked_or_error, gross, make_client, parse_it_decimal, pick_by_city
from .base import SourceError

BASE = "https://www.spedirecomodo.it"
START = BASE + "/cms/ioinvio/"

_CARD = re.compile(r'<form action="/Shipping/ShipCouriers".*?</form>', re.S)
_TITLE = re.compile(r"couriers-title[^>]*>\s*(.*?)\s*<br", re.S)
_CARRIER = re.compile(r"font-weight:700[^>]*>\s*([^<]+?)\s*</span>")
_PRICE = re.compile(r'bestPriceSort">\s*([\d.,]+)\s*<', re.S)
_HOURS = re.compile(r"(\d+)\s*/\s*(\d+)\s*h", re.I)
_DAYS = re.compile(r"(\d+)\s*/\s*(\d+)\s*g", re.I)


def _days(service: str) -> tuple[int | None, int | None]:
    if m := _HOURS.search(service):
        return math.ceil(int(m[1]) / 24), math.ceil(int(m[2]) / 24)
    if m := _DAYS.search(service):
        return int(m[1]), int(m[2])
    return None, None


def parse_offers(html: str) -> list[Offer]:
    """One <form> per courier. Prices are net of VAT; business-only (P.IVA) cards are skipped
    because a private sender cannot buy them."""
    cards = _CARD.findall(html)
    if not cards:
        if "IVA Escl" in html:
            raise SourceError("changed", "prices are present but the card markup changed")
        return []
    offers: list[Offer] = []
    for card in cards:
        if "Partita IVA certificata" in card:
            continue
        price, title, carrier = _PRICE.search(card), _TITLE.search(card), _CARRIER.search(card)
        if not (price and title and carrier):
            raise SourceError("changed", "courier card without price, service or carrier")
        service = unescape(re.sub(r"<[^>]+>|\s+", " ", title.group(1))).strip()
        lo, hi = _days(service)
        offers.append(
            Offer(
                source="spedirecomodo",
                carrier=unescape(carrier.group(1)).strip(),
                service=service,
                price_eur=gross(
                    parse_it_decimal(price.group(1))
                    if "," in price.group(1)
                    else float(price.group(1))
                ),
                delivery_days_min=lo,
                delivery_days_max=hi,
                url=START,
            )
        )
    return offers


class SpedireComodoSource:
    name = "spedirecomodo"

    async def _locality(self, client: httpx.AsyncClient, cap: str, city: str) -> dict:
        r = await client.post(
            f"{BASE}/Shipping/GetAddress",
            data={"dataType": "json", "nazione": "IT", "terminericerca": cap},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        blocked_or_error(r, "GetAddress")
        found = [d for d in r.json() if str(d.get("CodicePostale")) == cap]
        if not found:
            raise SourceError("empty", f"unknown postal code {cap}")
        return pick_by_city(found, city, "Localita")

    async def quote(self, request: QuoteRequest) -> list[Offer]:
        async with make_client() as client:
            start = await client.get(START)
            blocked_or_error(start, "start")
            tok = await client.get(
                f"{BASE}/Home/GetAntiforgeryToken", headers={"X-Requested-With": "XMLHttpRequest"}
            )
            blocked_or_error(tok, "antiforgery")
            token = (tok.json() or {}).get("token")
            if not token:
                raise SourceError("changed", "anti-forgery token missing")

            x = await self._locality(client, request.sender.postal_code, request.sender.city)
            y = await self._locality(client, request.recipient.postal_code, request.recipient.city)
            p = request.parcel
            form = {
                "__RequestVerificationToken": token,
                "PackageTipoCollo": "0",
                "PackageNazioneNome": "Italy",
                "PackageXNazione": "IT",
                "PackageXSelectedCap": x["Display"],
                "PackageXCap": request.sender.postal_code,
                "PackageXIdLocalita": str(x["Id"]),
                "PackageYNazione": "IT",
                "PackageYSelectedCap": y["Display"],
                "PackageYCap": request.recipient.postal_code,
                "PackageYIdLocalita": str(y["Id"]),
                "PackagePeso": f"{p.weight_kg:g}",
                "PackageHeight": f"{p.height_cm:g}",
                "PackageWidth": f"{p.width_cm:g}",
                "PackageDepth": f"{p.length_cm:g}",
            }
            r = await client.post(BASE + "/", data=form, headers={"Referer": START})
            blocked_or_error(r, "courier list")
            return parse_offers(r.text)
