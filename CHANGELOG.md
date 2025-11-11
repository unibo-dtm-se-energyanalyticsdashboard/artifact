# Changelog

## [0.2.0] - 2025-11-11

### Added

* Introduced **unit tests** for pipeline range computation (`test_pipeline_unit.py`).
* Added **smoke tests** for pipeline and dashboard initialization.
* Created a dedicated **logs/** directory for structured log storage.
* Implemented detailed **logging** across ingestion and pipeline modules for debugging and monitoring.

### Improved

* Enhanced `pipeline.py` with consistent log formatting and execution tracing.
* Updated **README.md** to reflect new test and logging architecture.
* CI configuration updated to integrate testing and coverage in automated workflows.

---

## [0.1.0] - 2025-11-07

### Added

* Initial release of **Energy Analytics Dashboard**.
* Data fetching integrated via **ENTSO-E API** using `entsoe-py`.
* PostgreSQL connection implemented with **SQLAlchemy**.
* ETL pipeline added for data aggregation and caching.
* Interactive dashboard built using **Dash** and **Plotly**, including:

  * KPI cards for energy metrics.
  * Tabs for different visualizations.
  * Support for both **full-year** and **last-10-days** data modes.
* Environment configuration using `.env` and `.env.example`.
* Project management and packaging via **Poetry**.
* CI/CD and development workflow configured for future releases.
