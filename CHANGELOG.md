# Changelog

## [1.0.0] - 2025-11-07

### Added
- Initial release of **Energy Analytics Dashboard**.
- Data fetching integrated via **ENTSO-E API** using `entsoe-py`.
- PostgreSQL connection implemented with **SQLAlchemy**.
- ETL pipeline added for data aggregation and caching.
- Interactive dashboard built using **Dash** and **Plotly**, including:
  - KPI cards for energy metrics.
  - Tabs for different visualizations.
  - Support for both **full-year** and **last-10-days** data modes.
- Environment configuration using `.env` and `.env.example`.
- Project management and packaging via **Poetry**.
- CI/CD and development workflow configured for future releases.
