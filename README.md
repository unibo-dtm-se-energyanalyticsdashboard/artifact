Energy Analytics Dashboard (EDAS)

A modular Python project for data ingestion, processing, and visualization of European electricity data using ENTSO-E API, PostgreSQL, Pandas, Dash, and Poetry—all integrated under CI/CD automation via GitHub Actions.

Table of Contents

Overview & Main Features

Requirements (User Stories)

Design & Architecture (DDD)

Architectural Pattern: Hexagonal (Ports & Adapters)

Domain-Driven Design (DDD) Concepts

Modelling (UML)

Project Structure

Setup Instructions

Usage (Ingestion & Dashboard)

Testing (Validation)

CI/CD & DevOps

Versioning & Licensing

Future Work & Self-Evaluation

Overview & Main Features

The Energy Analytics Dashboard (EDAS) automates the full data pipeline—from fetching raw data from the European electricity market (ENTSO-E) to storing and visualizing it through an interactive web dashboard.

Main Features

Modular ETL Pipeline: A robust pipeline for Extracting, Transforming, and Loading data.

Adapters Architecture: Decoupled infrastructure (PostgreSQL, ENTSO-E API) from the core application logic.

Data Ingestion: Fetches consumption, generation (by source), and cross-border flow data from the ENTSO-E API.

Incremental Updates: Uses an UPSERT (On Conflict Do Update) strategy to handle duplicate data and ensure idempotency.

Interactive Dashboard: A web-based (Plotly Dash) interface with filterable KPIs, time-series charts, and production mix visualizations.

Automated Testing: Unit tests for core logic and smoke tests for pipeline/dashboard initialization (Validation).

Full CI/CD: Automated checks (linting, testing, coverage) and release deployment using GitHub Actions and semantic-release.

Dependency Management: Managed via Poetry for reproducible builds.

1. Requirements (User Stories)

This section captures the functional and non-functional requirements as user stories, matching the Requirements section of the checklist.

User Story 1: Data Ingestion (Admin)

As an Admin,

I want to run an ingestion pipeline for specific countries and date ranges,

So that the data is fetched from ENTSO-E and stored correctly in the PostgreSQL database.

Definition of Done:

Data for Consumption, Production, and Flows is fetched.

Timestamps are normalized to UTC.

Data is saved to the database.

Duplicate records (based on timestamp, country, etc.) are handled via UPSERT.

User Story 2: Dashboard Analytics (Analyst)

As an Energy Analyst,

I want to see aggregated KPIs (Total Consumption, Total Production, Net Balance),

So that I can quickly understand the overall energy situation.

Definition of Done:

KPIs are displayed in clearly marked cards.

KPIs update when the date or country filter changes.

User Story 3: Visual Analysis (Analyst)

As an Energy Analyst,

I want to visualize consumption vs. production on a time-series chart,

So that I can identify patterns and imbalances.

Definition of Done:

A line chart displays both metrics on the same timeline.

A stacked area chart shows the production mix (e.g., Solar, Wind).

A heatmap shows hourly consumption patterns.

2. Design & Architecture (DDD)

This section fulfills the Design, DDD, and Modelling sections of the checklist, justifying the architectural choices.

Architectural Pattern: Hexagonal (Ports & Adapters)

The system is designed using the Hexagonal Architecture (also known as Ports & Adapters), as discussed in [Unit-03.1]. This separates the core application logic from outside infrastructure (like the API or database).

Core Application (The "Hexagon"):

src/edas/pipeline.py: The Application Service that orchestrates the workflow.

src/edas/domain/: (Implicit in your models) The Domain Model representing energy data.

Ports (The Interfaces):

(Implicitly defined) A "Repository" port for saving data (upsert.py).

(Implicitly defined) A "Client" port for fetching data (entsoe_client.py).

Adapters (The Implementation):

src/edas/ingestion/entsoe_client.py: An Adapter that implements the client port using the entsoe-py library.

src/edas/db/ & src/edas/ingestion/upsert.py: Adapters that implement the repository port using SQLAlchemy and psycopg2.

src/edas/dashboard/ & src/edas/cli.py: Adapters that provide a user interface (Client).

Domain-Driven Design (DDD) Concepts

Bounded Contexts: The project is split into two primary Bounded Contexts:

Ingestion Context: Responsible for fetching, transforming, and persisting data. Its Ubiquitous Language includes terms like fetch, upsert, zone_key.

Analytics Context: Responsible for querying, aggregating, and visualizing data. Its Language includes KPI, mix, net_balance.

Patterns Used:

Repository: The upsert.py module acts as a Repository, abstracting the database persistence logic from the pipeline.

Adapter: entsoe_client.py is a classic Adapter, translating external API calls into data structures usable by our domain.

Modelling (UML)

(This section is a placeholder for you to add the diagrams required by the checklist.)

Class Diagram

(Placeholder for the Class Diagram, showing the main Entities like EnergyProduction, EnergyConsumption, and their relationship with the Countries lookup table.)

Sequence Diagram (Ingestion Pipeline)

(Placeholder for the Sequence Diagram, showing the flow for edas-ingest: cli.py -> pipeline.py -> entsoe_client.py (Adapter) -> upsert.py (Repository) -> db)

3. Project Structure

(This structure is updated from your original README.md to match your actual implementation.)

.
├── .github/workflows/
│   ├── check.yml           # Full CI: syntax, linting (mypy), unit tests, coverage
│   └── deploy.yml          # Automated release pipeline (semantic-release)
│
├── scripts/
│   ├── db_init.sh        # Initialize PostgreSQL schema
│   ├── db_dump.sh        # Dump database data (deliverable)
│   └── ingest.py         # Manual CLI entrypoint for ETL
│
├── sql/
│   └── 01_schema.sql       # DDL: tables for consumption, production, flows, countries
│
├── logs/                   # Centralized directory for log output
│   └── app.log
│
├── src/edas/
│   ├── __init__.py
│   ├── config.py           # Reads DB config & ENTSOE token from environment (.env)
│   ├── pipeline.py         # Main orchestration (Application Service)
│   ├── cli.py              # Poetry script entry points (edas-ingest, edas-dashboard)
│   ├── logging_config.py   # Centralized logging configuration
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py   # DB Adapter: SQLAlchemy engine connection
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── entsoe_client.py # API Adapter: Data fetching and cleaning
│   │   └── upsert.py        # Repository: Data upsert logic for PostgreSQL
│   │
│   └── dashboard/
│       ├── __init__.py
│       ├── queries.py      # Analytics: SQL and aggregation logic
│       └── app.py          # UI: Dash app layout and callbacks
│
├── tests/
│   ├── test_pipeline_unit.py   # Unit tests for _compute_range()
│   ├── test_pipeline_smoke.py  # Smoke test for pipeline (using Mocks)
│   └── test_dashboard_smoke.py # Smoke test for dashboard layout
│
├── .env                    # Environment variables (Ignored by Git)
├── .env.example            # Example configuration file
├── .gitignore
├── LICENSE                 # Apache 2.0 license
├── poetry.toml             # Poetry configuration
├── pyproject.toml          # Dependencies, metadata, and build configuration
├── poetry.lock             # Dependency lock file
├── requirements.txt        # Used only for CI setup (dependency for Poetry)
├── renovate.json           # Automated dependency updates
└── release.config.mjs      # Semantic-release configuration


4. Setup Instructions

1. Install Dependencies

Ensure poetry is installed.

# Install Poetry (if not present)
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

Run data ingestion via the Poetry script (edas-ingest defined in pyproject.toml):

Last 10 days (default mode):

poetry run edas-ingest --countries FR DE


Full year 2025 (for project requirement):

poetry run edas-ingest --mode full_2025 --countries FR DE


Run the Dashboard

poetry run edas-dashboard


Open http://127.0.0.1:8050 in your browser.

6. Testing (Validation)

This project uses unittest and pytest (via poe tasks) for automated testing.

Run all tests:

poetry run poe test


Run tests with coverage (required by checklist):

poetry run poe coverage-report


Test Coverage Results

(Placeholder: Paste your coverage report here, as required by the checklist: "the final coverage is reported")

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/edas/__init__.py                  0      0   100%
src/edas/cli.py                      ...
src/edas/config.py                   ...
src* *eda*d*shboard/__init__.py        ...
...
---------------------------------------------------------------
TOTAL                               ...         XX%


7. CI/CD & DevOps

check.yml: A GitHub Actions workflow that runs on every push/PR. It performs linting (MyPy), and runs the full test suite (unit and smoke) across multiple Python versions (3.10, 3.11, 3.12). Test coverage reports are uploaded as artifacts.

deploy.yml: A GitHub Actions workflow that triggers on merges to main. It uses semantic-release to automatically increment the version, generate a CHANGELOG.md, and (if configured) publish the edas package to PyPI.

8. Versioning & Licensing

Versioning: This project uses Semantic Versioning (SemVer), automated via semantic-release and Conventional Commits.

License: Distributed under the Apache License 2.0.

Justification (Checklist Requirement): The Apache-2.0 license was chosen because it is a permissive, industry-standard license that is compatible with the project's dependencies (like pandas and dash). It allows for widespread use while protecting against patent claims, making it suitable for a data analytics tool.

9. Future Work & Self-Evaluation

(This section is required by the checklist.)

Self-Evaluation

(Placeholder: Add your self-evaluation here. E.g., "The integration of semantic-release was complex but successful. The DDD separation between ingestion and upsert logic could be further improved by introducing explicit Domain Entities instead of relying only on DataFrames.")

Future Work

Implement explicit Domain Model classes (Entities/Value Objects) instead of passing DataFrames between layers.

Add more comprehensive unit tests for upsert.py using a mocked database connection to test conflict handling.

Expand the dashboard to include Optional (Part 1) cross-border flow analysis.