"""Parsers run against real answers captured from each site (trimmed), no network."""

import json
from pathlib import Path

import pytest
from shipmentfinder_backend.sources import iospedisco, paccofacile, spedirecomodo
from shipmentfinder_backend.sources.base import SourceError

FIX = Path(__file__).parent / "fixtures"


def test_paccofacile_parses_gross_prices_and_days():
    offers = paccofacile.parse_offers(
        json.loads((FIX / "paccofacile_validation.json").read_text("utf8"))
    )
    assert len(offers) == 4
    first = offers[0]
    assert (first.carrier, first.service, first.price_eur) == ("Inpost", "Point To Point", 5.75)
    assert first.delivery_days_max == 3


def test_paccofacile_site_rejection_is_named_not_changed():
    payload = {
        "header": {"status": "ERROR", "notification": {"messages": {"pickup": ["required"]}}},
        "data": [],
    }
    with pytest.raises(SourceError) as e:
        paccofacile.parse_offers(payload)
    assert e.value.status == "error" and "pickup" in e.value.detail


def test_paccofacile_missing_services_means_layout_changed():
    with pytest.raises(SourceError) as e:
        paccofacile.parse_offers({"header": {"status": "OK"}, "data": {}})
    assert e.value.status == "changed"


def test_iospedisco_reads_analytics_items_and_adds_vat():
    offers = iospedisco.parse_offers((FIX / "iospedisco_prices.html").read_text("utf8"))
    by = {(o.carrier, o.service): o.price_eur for o in offers}
    assert len(offers) == 8
    assert by[("Poste Italiane", "Poste Delivery")] == pytest.approx(8.48 * 1.22, abs=0.01)
    assert by[("Tnt", "Tnt")] == pytest.approx(14.25 * 1.22, abs=0.01)


def test_iospedisco_unrecognisable_page_is_changed():
    with pytest.raises(SourceError) as e:
        iospedisco.parse_offers("<html>hello</html>")
    assert e.value.status == "changed"


def test_spedirecomodo_skips_business_only_and_adds_vat():
    offers = spedirecomodo.parse_offers((FIX / "spedirecomodo_couriers.html").read_text("utf8"))
    carriers = {o.carrier for o in offers}
    assert "BRT Pro" not in carriers  # P.IVA only: a private sender cannot buy it
    brt = next(o for o in offers if o.carrier == "BRT")
    assert brt.price_eur == pytest.approx(7.65 * 1.22, abs=0.01)
    assert (brt.delivery_days_min, brt.delivery_days_max) == (1, 2)


def test_spedirecomodo_prices_without_cards_is_changed_but_no_prices_is_empty():
    with pytest.raises(SourceError):
        spedirecomodo.parse_offers("<html>IVA Escl. 6,55</html>")
    assert spedirecomodo.parse_offers("<html>nessun servizio</html>") == []
