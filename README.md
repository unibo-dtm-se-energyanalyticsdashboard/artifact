# Energy Analytics Dashboard

A modular Python project for data ingestion, processing, and visualization of European electricity data using ENTSO-E API, PostgreSQL, Pandas, Dash, and Poetry — all integrated under CI/CD automation via GitHub Actions.

---

## Overview

The Energy Analytics Dashboard automates the full data pipeline — from fetching raw data from the European electricity market (ENTSO-E) to storing and visualizing it through an interactive web dashboard.

It supports:

* Fetching real-time and historical data from the ENTSO-E Transparency Platform.
* Two operating modes for ingestion:

  * `--mode full_2025` → Full dataset for 2025.
  * Default mode (no flag) → Last 10 days of data.
* Data persistence in a structured PostgreSQL database.
* Interactive analytics dashboard built with Plotly Dash.
* Integrated logging for monitoring pipeline execution and debugging.
* Automated testing for ingestion, pipeline, and dashboard components.

---

## Main Features

* Modular ETL (Extract–Transform–Load) pipeline
* PostgreSQL integration via SQLAlchemy
* ENTSO-E API client for energy data (consumption, generation, cross-border flows)
* Automated orchestration of ingestion modes (full-year or 10-day rolling window)
* Comprehensive logging system for tracing and debugging
* Unit and smoke tests for key pipeline functions
* Interactive Dash-based dashboard with KPIs, time series, production mix, and flow analytics
* Automated testing & CI with GitHub Actions
* Dependency management with Poetry
* Versioning & release automation via semantic-release

---

## Project Structure

```text
.
├── .github/workflows/
│   ├── check.yml           # Full CI: syntax, linting (mypy), unit tests, coverage
│   └── deploy.yml          # Automated release pipeline (semantic-release)
│
├── artifact/
│   ├── scripts/
│   │   ├── db_init.sh      # Initialize PostgreSQL schema
│   │   └── ingest.py       # CLI entrypoint for ETL (modes: full_2025 | last_10_days)
│   └── sql/
│       └── 01_schema.sql   # DDL: tables for consumption, production, flows, countries
│
├── logs/                   # Centralized directory for log output from pipeline and ingestion
│   └── pipeline.log        # Example log file generated during ETL runs
│
├── src/edas/
│   ├── __init__.py
│   ├── config.py           # Reads DB config & ENTSOE token from environment (.env)
│   ├── pipeline.py         # Main orchestration of ETL workflow + logging setup
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py   # SQLAlchemy engine connection using environment variables
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── entsoe_client.py # Data fetching from ENTSO-E API via entsoe-py
│   │   └── upsert.py        # Data upsert logic for PostgreSQL tables
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── queries.py      # SQL and aggregation logic for dashboard components
│       └── app.py          # Dash UI with KPI cards + tabs (time series, mix, flows, tables)
│
├── tests/
│   ├── test_pipeline_unit.py   # Unit tests for _compute_range() and validation logic
│   ├── test_pipeline_smoke.py  # Smoke test for minimal pipeline execution
│   └── test_dashboard_smoke.py # Dashboard smoke test for layout validation
│
├── .env                    # Environment variables (not tracked in Git)
├── .env.example            # Example configuration file
├── .gitignore
├── LICENSE                 # Apache 2.0 license
├── poetry.toml             # Poetry configuration
├── pyproject.toml          # Dependencies, metadata, and build configuration
├── poetry.lock             # Dependency lock file
├── requirements.txt        # Used for CI setup before Poetry
├── renovate.json           # Automated dependency updates
└── release.config.mjs      # Semantic-release configuration
```

---

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
poetry install
```

### 2. Set up the database

Make sure PostgreSQL is running, and the `.env` file contains your credentials:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_analytics
ENTSOE_API_KEY=your_entsoe_token
```

Initialize schema:

```bash
bash artifact/scripts/db_init.sh
```

---

## Data Ingestion

Run data ingestion via the CLI tool:

**Last 10 days (default):**

```bash
poetry run python artifact/scripts/ingest.py --countries FR DE
```

**Full year 2025:**

```bash
poetry run python artifact/scripts/ingest.py --mode full_2025 --countries FR DE
```

Logs for ingestion and pipeline runs are saved automatically in the `/logs` directory.

---

## Run the Dashboard

```bash
poetry run python -m src.edas.dashboard.app
```

Open [http://127.0.0.1:8050](http://127.0.0.1:8050) in your browser.
You’ll see:

* Top section with KPIs (load, generation, net flow)
* Interactive tabs for Time Series, Mix, and Country Comparisons.

---

## Testing

Run all tests locally:

```bash
poetry run python -m unittest discover -v
```

Tests include:

* **Unit tests** — for pipeline components (range logic, data checks)
* **Smoke tests** — verifying pipeline and dashboard initialization

Tests are automatically executed in GitHub Actions on every push or pull request.

---

## CI/CD Integration

* **check.yml** → Comprehensive CI (syntax, linting, unit tests, coverage)
* **deploy.yml** → Automated semantic-release deployment to PyPI or GitHub
* **Logging output** and **test coverage** are uploaded as artifacts for inspection.

---

## Versioning & Releases

Uses Semantic Versioning (SemVer) via commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) standard.
Automatic release to PyPI is triggered upon merging into `main`.

---

## License

Distributed under the Apache License 2.0.
See the [LICENSE](LICENSE) file for details.
