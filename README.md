<<<<<<< HEAD
# Snip — URL Shortener

FastAPI + TiDB (MySQL-compatible) URL shortener with click analytics, a REST API with
auto-generated Swagger docs, and a small HTML/CSS/JS frontend.
## DEMO
<img src="assets/Screenshot 2026-07-26 232605.png" width="800">
<img src="assets/Screenshot 2026-07-26 232618.png" width="800">
## Features

- Shorten any URL, with an optional custom alias
- Redirect short links to their original URL
- Click counting + `last_accessed` timestamp per link
- Analytics endpoint per link, plus an overall summary
- List / delete links
- Interactive Swagger UI at `/docs`
- Frontend at `/` to try it all without touching the API directly

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, PyMySQL
- **Database:** TiDB (or any MySQL 5.7+/8.0-compatible database) — TiDB speaks the MySQL
  wire protocol, so the same `mysql+pymysql` SQLAlchemy driver works against either.
- **Frontend:** plain HTML/CSS/JS (no build step), served by FastAPI's `StaticFiles`

## Project structure

```
url-shortener/
├── app/
│   ├── main.py        # FastAPI app & routes
│   ├── database.py     # SQLAlchemy engine/session (TiDB/MySQL connection)
│   ├── models.py        # URL ORM model (short_code is unique + indexed)
│   ├── schemas.py        # Pydantic request/response models
│   └── utils.py           # short code generation (base62)
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt
├── .env.example
└── run.py
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the database**

   Copy `.env.example` to `.env` and fill in your TiDB (or MySQL) credentials:

   ```bash
   cp .env.example .env
   ```

   - **TiDB Cloud (Serverless, free tier):** create a cluster at
     https://tidbcloud.com, then copy the host/user/password from the cluster's
     "Connect" page. Keep `DB_SSL=true`.
   - **Local MySQL:** set `DB_HOST=127.0.0.1`, `DB_PORT=3306`, your local
     credentials, and `DB_SSL=false`. Create the database first:
     `CREATE DATABASE url_shortener;`
   - **Local TiDB (via TiUP playground):** `tiup playground` starts a
     MySQL-compatible endpoint on `127.0.0.1:4000` with no password by default.

   The app creates the `urls` table automatically on first run.

3. **Run the server**

   ```bash
   python run.py
   ```

   or

   ```bash
   uvicorn app.main:app --reload
   ```

4. **Open it**

   - Frontend: http://localhost:8000/
   - Swagger docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API reference

| Method | Path                          | Description                          |
|--------|-------------------------------|---------------------------------------|
| POST   | `/api/shorten`                | Create a short URL                    |
| GET    | `/{short_code}`               | Redirect to the original URL (307)    |
| GET    | `/api/urls`                   | List all shortened URLs               |
| GET    | `/api/analytics/{short_code}` | Click count & timestamps for one link |
| GET    | `/api/stats/summary`          | Total links + total clicks            |
| DELETE | `/api/urls/{short_code}`      | Delete a shortened URL                |

### Example: create a short URL

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.anthropic.com/news", "custom_code": "news"}'
```

```json
{
  "short_code": "news",
  "short_url": "http://localhost:8000/news",
  "original_url": "https://www.anthropic.com/news",
  "clicks": 0,
  "created_at": "2026-07-25T12:00:00"
}
```

## Concepts this project demonstrates

- **CRUD** — create, read (list/redirect/analytics), and delete on the `urls` table
- **Unique IDs** — random base62 short codes, checked for collisions before insert,
  with an optional custom alias path validated separately
- **Indexing** — `short_code` has a unique index so redirect lookups stay fast as the
  table grows, instead of a full table scan
- **Redirects** — `GET /{short_code}` issues an HTTP 307 redirect and increments the
  click counter atomically within the same request
=======
# Snip
Shorten a long URL.
>>>>>>> ba4380eb7fbee46881491e9af9aca6bbd2a415ea
