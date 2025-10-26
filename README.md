# **HexaOSINT - A modular OSINT API**

HexaOSINT is an OSINT API that combines multiple methods (text and image inputs) to search social media and files across the web. It processes the provided data to generate queries and retrieve relevant links from various sources. The architecture follows a **package-by-feature** structure, separating controllers, routes, schemas, and services.

---

## **Features**

- Accepts a search target (name, domain, type, categories, etc.) via validated request schemas.
- **Text-based OSINT searches** with configurable categories (social, files, logs).
- **Image-based face recognition searches** using FaceCrawler API integration.
- Generates search engine dorks based on the provided categories using strategic patterns.
- Executes searches using SerpAPI with support for multiple search engines (Google, Bing, DuckDuckGo).
- Returns structured search results with metadata.
- Designed to integrate with a PostgreSQL database for persisting:
  - Search history and scan metadata
  - Processed results with scoring and classification
  - Image search results and face recognition data

---

## **Project Structure**

```
source/
│
├── auth/               # JWT authentication configuration
├── database/           # Database configuration and models
│   ├── models/         # SQLAlchemy models (ScanHistory, TargetResult)
│   └── base.py         # Base model and database session
├── enums/              # Enum definitions for request validation
│   ├── target_type.py  # Target types (company, person)
│   ├── search_type.py  # Search types (google_search)
│   ├── engine_type.py  # Search engines (google, bing, duckduckgo)
│   └── country_type.py # Country selection (Brazil, US, UK, etc.)
├── modules/
│   └── target/          # Target-related features
│       ├── controllers/ # Business logic for targets
│       ├── routes/      # FastAPI routes (text-search, image-search)
│       └── schemas/     # Pydantic schemas for requests/responses
├── services/            # Core services
│   ├── dorkgen/        # Dork query generation strategies
│   ├── facecrawler/    # Face recognition search service
│   └── serpapi/        # Search engine integration
├── main.py             # Application entry point
└── ...
```

---

## **API Endpoints**

### **Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT + refresh tokens
- `POST /auth/refresh` - Refresh access token using refresh token
- `POST /auth/logout` - Logout and revoke tokens
- `GET /auth/me` - Get current user info
- `GET /auth/verify-token` - Verify JWT token validity

### **Text Search** (Requires Authentication)
- `POST /target/text-search` - Perform text-based OSINT searches
  - Supports multiple categories: social, files, logs
  - Configurable search engines and countries
  - Target types: company, person

### **Image Search** (Requires Authentication)
- `POST /target/image-search/send` - Upload image for face recognition
- `POST /target/image-search/receive` - Retrieve face recognition results

---

## **Database Schema**

The main entities and relationships:

- **users** — User accounts and authentication:
  - First name, last name, email, hashed password
  - Active status and admin privileges
  - Creation and last login timestamps

- **refresh_tokens** — Refresh tokens for token renewal:
  - Secure tokens for access token refresh
  - Device and IP tracking
  - Expiration and revocation management

- **scan_history** — Each scan execution with metadata:
  - User association (foreign key)
  - Search type, engine, query
  - Image metadata for face searches
  - Status tracking and timestamps

- **target_results** — Parsed results from scans:
  - Title, link, snippet, image URLs
  - Source type classification
  - Scoring and processing status
  - Relationship to scan history

---

## **Example Flow**

### **Authentication Flow:**
1. **Register user** via `/auth/register` with first_name, last_name, email, and password.
2. **Login** via `/auth/login` to receive JWT access token and refresh token.
3. **Use access token** in `X-User-JWT` header for protected endpoints.
4. **Refresh token** via `/auth/refresh` when access token expires.
5. **Logout** via `/auth/logout` to revoke tokens.

### **Text Search Flow:**
1. **Authenticate** with JWT token in `X-User-JWT` header.
2. **Send request** with target data and categories (social, files, logs).
3. **Build dork query** using `DorkGen` service with strategic patterns.
4. **Execute search** via `SerpAPIController` with selected engine.
5. **Return structured results** as JSON with metadata.
6. **Persist results** to PostgreSQL associated with authenticated user.

### **Image Search Flow:**
1. **Authenticate** with JWT token in `X-User-JWT` header.
2. **Upload image** via `/target/image-search/send` endpoint.
3. **Process image** using FaceCrawler service integration.
4. **Track progress** and retrieve results via `/target/image-search/receive`.
5. **Store results** in database with image metadata and user association.

---

## **Tech Stack**

- **FastAPI** — Web framework with automatic API documentation.
- **Pydantic** — Request/response validation and serialization.
- **SQLAlchemy** — ORM for PostgreSQL with relationship management.
- **SerpAPI** — Multi-engine search API integration (Google, Bing, DuckDuckGo).
- **FaceCrawler** — Face recognition and image search service.
- **JWT Authentication** — Secure endpoint access control with refresh tokens.
- **Refresh Tokens** — Secure token renewal and logout management.
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
# JWT Authentication
SECRET_AUTH_KEY=your_super_secret_jwt_key_here

# SerpAPI
SERPAPI_KEY=your_serpapi_key

# FaceCrawler API
FACECRAWLER_KEY=your_facecrawler_key
SITE_URL=https://facecrawler-api-url.com

# PostgreSQL Connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=osint_db

# Table Names
DB_TARGET_RESULT=target_results
DB_SCAN_HISTORY=scan_history
```

---

## **Authentication Setup**

Para configuração detalhada e uso da autenticação, consulte [AUTHENTICATION.md](source/AUTHENTICATION.md).

Para informações sobre refresh tokens, consulte [REFRESH_TOKENS.md](source/REFRESH_TOKENS.md).

---

## **License**

MIT License.
