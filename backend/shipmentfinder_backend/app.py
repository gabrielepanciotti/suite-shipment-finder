from __future__ import annotations

from collections.abc import Callable, Sequence

from fastapi import FastAPI
from suite_backend_core import create_app
from suite_backend_core.vista import MemoryPreferenceStore, make_vista_router
from suite_backend_core.vista_claims import make_claims_dependency

from .comparison import compare
from .errors import install_error_handlers
from .models import Comparison, QuoteRequest
from .sources.base import ShippingSource
from .sources.registry import default_sources
from .vista import load_vista_spec

SourceFactory = Callable[[], Sequence[ShippingSource]]


def build_app(sources: SourceFactory = default_sources) -> FastAPI:
    """`sources` is injectable: tests pass fakes, prod passes the real site bots."""
    app = create_app()
    install_error_handlers(app)
    app.include_router(
        make_vista_router(
            load_vista_spec(),
            MemoryPreferenceStore(),
            make_claims_dependency("shipmentfinder"),
            "shipmentfinder",
        )
    )

    @app.get("/api/sources")
    async def list_sources() -> dict[str, list[str]]:
        return {"sources": [s.name for s in sources()]}

    @app.post("/api/quotes", response_model=Comparison)
    async def quotes(request: QuoteRequest) -> Comparison:
        return await compare(request, sources())

    return app


app = build_app()
