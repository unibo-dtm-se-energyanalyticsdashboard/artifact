Energy Analytics Dashboard (EDAS)

A modular Python project for data ingestion, processing, and visualization of European electricity data using ENTSO-E API, PostgreSQL, Pandas, Dash, and Poetry—all integrated under CI/CD automation via GitHub Actions.

1. Requirements & Specification

This section captures the functional requirements as User Stories, fulfilling the Requirements section of the checklist.

User Story 1: Data Ingestion (Admin)

As an Admin,

I want to run an ingestion pipeline for specific countries (FR, DE) and a defined date range (e.g., full_2025 or last_10_days),

So that the data is reliably fetched from ENTSO-E and stored in the PostgreSQL database.

Definition of Done (Acceptance Criteria):

Data for Consumption, Production (by source), and Flows is fetched (entsoe_client.py).

Timestamps are normalized to UTC (to_utc_naive).

Data is saved to the database.

Duplicate records (based on timestamp, country, etc.) are handled via UPSERT (upsert.py).

User Story 2: Dashboard Analytics (Analyst)

As an Energy Analyst,

I want to see aggregated KPIs (Total Consumption, Total Production, Net Balance) in an interactive dashboard,

So that I can quickly understand the overall energy situation.

Definition of Done (Acceptance Criteria):

KPIs are displayed in clearly marked cards (_kpi_card).

KPIs update when the date or country filter changes (update_kpis callback).

All analytic queries (queries.py) execute successfully.

User Story 3: Visual Analysis (Analyst)

As an Energy Analyst,

I want to visualize consumption vs. production and the production mix,

So that I can identify patterns and imbalances.

Definition of Done (Acceptance Criteria):

A line chart displays Consumption vs. Production (tab == "overview").

A stacked area chart shows the Production Mix by source type (tab == "mix").

A heatmap shows hourly consumption patterns (tab == "heat").

Data tables for daily summaries and raw flows are available (tab == "tables").

2. Design & Architecture (DDD)

This section fulfills the Design, DDD, and Modelling sections of the checklist.

Architectural Pattern: Hexagonal (Ports & Adapters)

The system is designed using the Hexagonal Architecture (Ports & Adapters). This isolates the core application logic (pipeline.py) from infrastructure details (the API, the Database, the UI). This is achieved through specific adapter modules:

Core Application (The "Hexagon"):

src/edas/pipeline.py: The Application Service that orchestrates the workflow.

(Implicit Domain): The data structures (DataFrames) representing energy data.

Primary Adapters (Drivers - User Side):

src/edas/dashboard/app.py: Implements the Web UI (Client).

src/edas/cli.py: Implements the Command-Line Interface (Client).

Secondary Adapters (Driven - Infrastructure Side):

src/edas/ingestion/entsoe_client.py: An Adapter that implements the external API client port using the entsoe-py library.

src/edas/db/connection.py & src/edas/ingestion/upsert.py: An Adapter that implements the database repository port using SQLAlchemy and psycopg2.

Domain-Driven Design (DDD) Concepts

Bounded Contexts: The project is split into two primary Bounded Contexts:

Ingestion Context: Responsible for fetching, transforming, and persisting data. Its Ubiquitous Language includes terms like fetch_production, upsert, zone_key, to_utc_naive.

Analytics Context: Responsible for querying, aggregating, and visualizing data. Its Language includes KPIs, production_mix, net_balance, daily_summary.

Patterns Used:

Repository: The upsert.py module is the Repository Pattern implementation. It abstracts the database persistence logic (ON CONFLICT DO UPDATE) from the main pipeline.

Adapter: entsoe_client.py is a classic Adapter, translating external API calls into data structures usable by our application.

Modelling (UML)

This section describes the key models as required by the checklist.

Class Diagram (Database Schema)

The domain model is represented by the database schema (01_schema.sql). The main entities are countries, energy_consumption, energy_production, and cross_border_flow. The countries table acts as a lookup table, while the other three are time-series data tables linked via foreign keys to countries.

Sequence Diagram (Ingestion Pipeline)

A sequence diagram for the edas-ingest command would show the following flow:

User executes edas-ingest.

cli.py parses arguments and calls pipeline.py (run_pipeline).

pipeline.py (Application Service) calls db/connection.py (get_engine).

pipeline.py calls ingestion/entsoe_client.py (fetch_consumption, fetch_production, etc.) to get data (API Adapter).

pipeline.py calls ingestion/upsert.py (Repository) to save the data.

upsert.py uses the connection to execute batch INSERT ON CONFLICT commands on the database.

3. Project Structure

This structure reflects the actual file layout, organized by feature (scripts, SQL, source code, tests).

. (Project Root)
├── .github/workflows/
│   ├── check.yml           # Full CI: syntax, linting (mypy), unit tests, coverage
│   └── deploy.yml          # Automated release pipeline (semantic-release)
│
├── scripts/
│   ├── db_init.sh          # Initialize PostgreSQL schema (Runs 01_schema.sql)
│   ├── db_dump.sh          # Create data-only dump (Deliverable)
│   └── ingest.py           # Manual CLI entrypoint for ETL (for debugging)
│
├── sql/
│   └── 01_schema.sql       # DDL: tables for consumption, production, flows, countries
│
├── logs/
│   └── app.log             # Log file (Ignored by Git)
│
├── src/edas/
│   ├── __init__.py
│   ├── config.py           # Reads DB config & ENTSOE token from environment (.env)
│   ├── pipeline.py         # Main orchestration (Application Service)
│   ├── cli.py              # Poetry script entry points (edas-ingest, edas-dashboard)
│   ├── logging_config.py   # Centralized logging configuration
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py   # DB Adapter: SQLAlchemy engine connection
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── entsoe_client.py # API Adapter: Data fetching and cleaning
│   │   └── upsert.py        # Repository: Data upsert logic for PostgreSQL
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── queries.py      # Analytics: SQL and aggregation logic
│       └── app.py          # UI: Dash app layout and callbacks
│
├── tests/
│   ├── __init__.py
│   ├── test_pipeline_unit.py   # Unit tests for _compute_range()
│   ├── test_pipeline_smoke.py  # Smoke test for pipeline (using Mocks)
│   └── test_dashboard_smoke.py # Smoke test for dashboard layout
│
├── .env                    # Environment variables (Ignored by Git)
├── .env.example            # Example configuration file
├── .gitignore
├── LICENSE                 # Apache 2.0 license
├── CHANGELOG.md            # (Auto-generated by semantic-release)
├── poetry.toml             # Poetry configuration (e.g., test-pypi source)
├── pyproject.toml          # Dependencies, metadata, and build configuration
├── poetry.lock             # Dependency lock file
├── requirements.txt        # Used *only* for CI setup (installs Poetry)
├── renovate.json           # Automated dependency updates (Renovate Bot)
└── release.config.mjs      # Semantic-release configuration


4. Setup Instructions

1. Install Dependencies

Ensure poetry is installed.

# Install Poetry (if not present)
# (Note: requirements.txt is only used by CI to install poetry)
pip install poetry
# Install project dependencies
poetry install


2. Set Up Environment

Create a .env file in the project root (copy from .env.example) and fill in your credentials:

DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_analytics
ENTSOE_API_KEY=your_entsoe_token


3. Initialize Database

Make sure PostgreSQL is running and the user/database exists.

# Activate the virtual environment
poetry shell
# Run the schema initialization script
bash scripts/db_init.sh


5. Usage (Ingestion & Dashboard)

Data Ingestion

Run data ingestion via the Poetry script (edas-ingest defined in pyproject.toml and src/edas/cli.py):

Last 10 days (default mode):

poetry run edas-ingest --countries FR DE


Full 2025 Data (for project requirement):

poetry run edas-ingest --mode full_2025 --countries FR DE


Run the Dashboard

Run the dashboard via the Poetry script (edas-dashboard):

poetry run edas-dashboard


Open http://127.0.0.1:8050 in your browser.

6. Testing (Validation)

This project uses unittest (and pytest via poe) for automated testing, fulfilling the Validation checklist requirements.

Run all tests (using the poe task defined in pyproject.toml):

poetry run poe test


Run tests with coverage (required by checklist):

poetry run poe coverage-report


Test Coverage Results

(Placeholder: Paste your coverage report here, as required by the checklist: "the final coverage is reported")

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/edas/__init__.py                  ...
src/edas/cli.py                      ...
src/edas/config.py                   ...
...
---------------------------------------------------------------
TOTAL                               ...         XX%


7. CI/CD & DevOps

check.yml: A GitHub Actions workflow that runs on every push/PR. It performs linting (MyPy), and runs the full test suite (unit and smoke) across multiple Python versions (3.10, 3.11, 3.12). Test coverage reports are uploaded as artifacts.

deploy.yml: A GitHub Actions workflow that triggers on merges to main. It uses semantic-release (configured in release.config.mjs) to automatically increment the version, generate a CHANGELOG.md, and (if configured) publish the edas package to PyPI.

Renovate: renovate.json is configured to automatically create Pull Requests for dependency updates, ensuring the project stays current.

8. Versioning & Licensing

Versioning: This project uses Semantic Versioning (SemVer), automated via semantic-release and Conventional Commits.

License: Distributed under the Apache License 2.0 (see LICENSE file).

Justification (Checklist Requirement): The Apache-2.0 license was chosen because it is a permissive, industry-standard license compatible with the project's dependencies (like pandas and dash). It allows for widespread use while protecting against patent claims, making it suitable for a data analytics tool.

9. Future Work & Self-Evaluation

(This section is required by the checklist.)

Self-Evaluation

This project successfully implements a full, automated ETL and analytics pipeline. The architecture (Hexagonal) correctly separates concerns (API, DB, UI) using Adapters. The CI/CD pipeline is robust, integrating linting, multi-python testing, and automated releases.

The main area for improvement is the explicitness of the Domain Model; currently, domain logic is embedded in pandas.DataFrame structures passed between layers. The logging configuration was also refactored during development to correctly handle initialization in both the CI environment (fixing a FileNotFoundError) and the local app.

Future Work

Refactor to Explicit Domain Model: Implement formal Port interfaces (Abstract Base Classes) for EnergyRepository and EntsoeClient. Refactor the pipeline to pass explicit Domain Model classes (e.g., EnergyRecord dataclasses) instead of raw DataFrames.

Comprehensive Unit Tests: Expand unit test coverage, especially for the upsert.py logic, using pytest-mock to simulate database transactions and conflict handling.

Expand Features: Add the optional (Part 1) cross-border flow analysis (e.g., net import/export) to the Dashboard.