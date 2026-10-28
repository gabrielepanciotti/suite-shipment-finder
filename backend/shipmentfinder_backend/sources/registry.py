"""The sources the node talks to in production. Add a site here once its bot exists."""

from __future__ import annotations

from .base import ShippingSource
from .iospedisco import IoSpediscoSource
from .paccofacile import PaccofacileSource
from .spedirecomodo import SpedireComodoSource


def default_sources() -> list[ShippingSource]:
    return [PaccofacileSource(), IoSpediscoSource(), SpedireComodoSource()]
