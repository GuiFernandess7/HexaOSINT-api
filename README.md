# **HexaOSINT - An modular OSINT API**

A modular API for performing OSINT (Open Source Intelligence) searches, building dork queries, and retrieving structured results from search engines such as Google via SerpAPI.
The architecture follows a **package-by-feature** structure, separating controllers, routes, schemas, and services.

---

## **Features**

- Accepts a search target (name, domain, type, categories, etc.) via validated request schemas.
- Generates search engine dorks based on the provided categories.
- Executes searches using SerpAPI.
- Returns structured search results.
- Designed to integrate with a PostgreSQL database for persisting:

  - Search history
  - Processed results

---

## **Project Structure**

```
source/
│
├── database/            # Database configuration and models
├── enums/               # Enum definitions for request validation
├── modules/
│   └── target/          # Target-related features
│       ├── controllers/ # Business logic for targets
│       ├── routes/      # FastAPI routes
│       └── schemas/     # Pydantic schemas
├── services/            # Core services (DorkGen, SerpAPI integration, etc.)
├── main.py               # Application entry point
└── ...
```

---

## **Database Schema**

The main entities and relationships:

- **scan_history** — Each scan execution and its metadata.
- **processed_results** — Parsed results from scans.

---

## **Example Flow**

1. **Send request** with target data and categories.
2. **Build dork query** using `DorkGen` service.
3. **Execute search** via `SerpAPIController`.
4. **Return structured results** as JSON.
5. (Planned) Persist results to PostgreSQL following the relationship chain:

---

## **Tech Stack**

- **FastAPI** — Web framework.
- **Pydantic** — Request/response validation.
- **SQLAlchemy** — ORM for PostgreSQL.
- **SerpAPI** — Search API integration.
- **uv** — Modern Python package and environment manager.

---

## **Installation**

```bash
# Install dependencies from pyproject.toml
uv pip install -e .

# Or install without editable mode
uv pip install .
```

---

## **Running the API**

```bash
uv run uvicorn source.main:app --reload
```

---

## **Environment Variables**

Create a `.env` file with:

```
# SerpAPI
SERPAPI_KEY=your_serpapi_key

# PostgreSQL Connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=osint_db

# Table Names
DB_TARGET=target
DB_TARGET_RESULTS=target_results
DB_SCAN_HISTORY=scan_history
DB_AUDIT_LOGS=audit_logs
```

---

## **License**

MIT License.
