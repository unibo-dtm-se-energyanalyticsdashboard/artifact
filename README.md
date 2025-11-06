#  Energy Analytics Dashboard

A Python-based project for the automated ingestion, processing, and visualization of European energy data.  
Developed as part of the **Software Engineering Project Work** at the **University of Bologna**, supervised by *Giovanni Ciatto*.

---

## Relevant features

- All project code contained within a single main package (`src/edas/`)
- Modular structure separating **ingestion**, **database**, **pipeline**, and **dashboard** logic
- Unit testing support via [`unittest`](https://docs.python.org/3/library/unittest.html)
- Data ingestion via [ENTSO-E API](https://transparency.entsoe.eu/)
- Data persistence using **PostgreSQL**
- Interactive visualization using **Plotly Dash**
- Automatic testing via **GitHub Actions**
- Environment and dependency management with **Poetry**
- Automatic release and semantic versioning via [`semantic-release`](https://semantic-release.gitbook.io)
- Automatic dependencies updates via [Renovate](https://docs.renovatebot.com/)

---

## Project structure

```bash
<root directory>
├── src/
│   └── edas/                # main package
│       ├── ingestion/       # ingestion logic (ENTSO-E data fetching)
│       ├── db/              # database connection and management
│       ├── dashboard/       # Dash app with KPIs and visualizations
│       ├── pipeline.py      # orchestration of data flow
│       └── __init__.py
│
├── scripts/                 # command-line entry scripts
│   └── ingest.py
│
├── tests/                   # test package (unittest-based)
│
├── .github/
│   └── workflows/           # CI/CD automation
│       ├── check.yml        # multi-OS and multi-version tests
│       ├── ci.yml           # CI workflow
│       └── deploy.yml       # automatic PyPI & GitHub release
│
├── pyproject.toml           # project configuration (Poetry)
├── requirements.txt         # bootstrap Poetry dependency
├── LICENSE                  # license file (MIT)
├── README.md                # project documentation
└── .env.example             # sample environment configuration
````

---

## Setup and usage

### 1️ Clone the repository

```bash
git clone https://github.com/unibo-dtm-se-energyanalyticsdashboard/artifact.git
cd artifact
```

### 2️ Install dependencies

```bash
pip install poetry
poetry install
```

### 3️ Configure environment variables

Create a `.env` file based on `.env.example`:

```bash
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_analytics
ENTSOE_API_KEY=your_entsoe_api_token
```

### 4️ Run data ingestion

```bash
poetry run python scripts/ingest.py --mode full_2025 --countries FR DE
```

### 5️ Launch the dashboard

```bash
poetry run python -m edas.dashboard.app
```

Then open the dashboard at:
 **[http://127.0.0.1:8050](http://127.0.0.1:8050)**

---

## Testing

Run tests locally:

```bash
poetry run python -m unittest discover -v -s tests
```

> Tests are automatically executed in CI (GitHub Actions)
> across multiple OS (Ubuntu, macOS, Windows) and Python versions (3.9 → 3.13).

---

## Versioning & release

This project follows **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH
```

| Type      | Description                              | Example |
| --------- | ---------------------------------------- | ------- |
| **MAJOR** | incompatible API or architecture changes | `1.0.0` |
| **MINOR** | new backward-compatible features         | `0.2.0` |
| **PATCH** | bug fixes or small improvements          | `0.1.1` |

Releases are managed automatically via **semantic-release** when commits reach the `main` branch.

Manual example:

```bash
poetry version patch     # or minor / major
git add pyproject.toml
git commit -m "chore(release): bump version to 0.1.0"
git tag -a v0.1.0 -m "release: v0.1.0"
git push origin main --tags
```

---

## CI/CD Pipelines

| Workflow       | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| **check.yml**  | Syntax validation, type checking, and unit tests             |
| **ci.yml**     | Multi-platform testing (Ubuntu, macOS, Windows)              |
| **deploy.yml** | Automated packaging & release to PyPI (via semantic-release) |

---

## Automatic dependency updates

This project uses [Renovate](https://docs.renovatebot.com/) to keep dependencies in `pyproject.toml` up to date.
Renovate automatically opens pull requests for updates and merges them if all tests pass.

Steps to enable Renovate:

1. Enable the Renovate GitHub App for this repository.
2. Allow PR auto-merging in your repo settings.
3. Verify CI pipelines (`check.yml`, `ci.yml`) pass before merge.

> Note: Renovate + Semantic Release may produce multiple automatic patch releases — this is expected.

---

## License

This project is distributed under the **MIT License**.
See the [LICENSE](./LICENSE) file for full details.

---

## Authors

* **Romin [Your Last Name]** — Developer
* **Supervisor:** [Giovanni Ciatto](https://ciatto.unibo.it), University of Bologna

---

## Acknowledgements

Developed as part of the
**Distributed and Pervasive Systems – Software Engineering Project Work (A.Y. 2024/2025)**,
following the official [Python Project Template](https://github.com/unibo-dtm-se) by *Giovanni Ciatto*.

```

---

