# ShipmentFinder

ShipmentFinder compares parcel-delivery quotes from multiple carriers and presents the available offers in one price-sorted list. It helps a private sender choose a service, but never purchases or creates a shipment.

## Features

- Queries independent HTTP-based shipping sources concurrently.
- Normalizes prices to VAT-inclusive EUR and filters business-only offers.
- Reports source failures separately from routes with no available service.
- Includes a FastAPI API and a React/Vite interface.

## Requirements

- Python 3.13
- Node.js 20 and npm
- The [Life framework](https://github.com/suite-life) checked out as a sibling directory named `Life` (it provides the shared `suite_*` and `@suite/*` packages).
- Docker and Docker Compose are optional.

## Quickstart

```bash
git clone <your-fork-url> shipment-finder
git clone https://github.com/suite-life.git Life
cd shipment-finder
cp .env.example .env

python3.13 -m venv .venv
.venv/bin/pip install ../Life/packages/shared ../Life/packages/backend-core -r backend/requirements.txt pytest
PYTHONPATH=backend .venv/bin/python -m uvicorn shipmentfinder_backend:app --reload --port 8000
```

In a second terminal:

```bash
cd shipment-finder/frontend
npm ci
npm run dev
```

For Docker, review `.env.example` and run `docker compose -f deploy/docker-compose.example.yml up --build`. The example is intended for local development with a sibling Life framework checkout.

## Tests

```bash
PYTHONPATH=backend .venv/bin/python -m pytest -q backend/tests
cd frontend && npm test -- --pool=forks --poolOptions.forks.maxForks=2 --poolOptions.forks.minForks=1 && npm run build
```

The CI workflow checks out the Life framework beside this repository. Set the repository variable `LIFE_FRAMEWORK_REPO` to use a fork; its default is `suite-life`.

## Configuration

| Variable | Purpose |
| --- | --- |
| `PORT` | Backend listen port. |
| `UVICORN_RELOAD` | Enable backend reload in development. |
| `VITE_BACKEND_PROXY_TARGET` | Backend URL used by the Vite development proxy. |
| `DATABASE_URL` | Optional database DSN for Alembic migrations. |
| `LIFE_FRAMEWORK_DIR` | Path to the sibling Life framework for Docker preparation. |

See [the Italian user guide](docs/guida.md) for usage details.

## License

MIT. See [LICENSE](LICENSE).
