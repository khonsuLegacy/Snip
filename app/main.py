import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import engine, get_db, Base
from .models import URL
from .schemas import URLCreateRequest, URLResponse, AnalyticsResponse
from .utils import generate_short_code

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Creates the `urls` table (with its unique index on short_code) if it
# doesn't exist yet. TiDB understands standard MySQL DDL.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener backed by TiDB/MySQL. "
    "Create short links, redirect, and track click analytics.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESERVED_PATHS = {"api", "docs", "redoc", "openapi.json", "static", "favicon.ico"}


def get_unique_short_code(db: Session, length: int = 6, attempts: int = 5) -> str:
    for _ in range(attempts):
        code = generate_short_code(length)
        exists = db.query(URL).filter(URL.short_code == code).first()
        if not exists:
            return code
    # Extremely unlikely fallback: grow the length and try once more
    return generate_short_code(length + 2)


@app.post("/api/shorten", response_model=URLResponse, tags=["URLs"])
def shorten_url(payload: URLCreateRequest, db: Session = Depends(get_db)):
    """Create a short URL for the given original_url. Optionally supply a
    custom_code instead of a randomly generated one."""
    if payload.custom_code:
        if payload.custom_code in RESERVED_PATHS:
            raise HTTPException(status_code=400, detail="That custom code is reserved.")
        existing = db.query(URL).filter(URL.short_code == payload.custom_code).first()
        if existing:
            raise HTTPException(status_code=409, detail="Custom code already in use.")
        code = payload.custom_code
    else:
        code = get_unique_short_code(db)

    url_entry = URL(short_code=code, original_url=str(payload.original_url), clicks=0)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)

    return URLResponse(
        short_code=url_entry.short_code,
        short_url=f"{BASE_URL}/{url_entry.short_code}",
        original_url=url_entry.original_url,
        clicks=url_entry.clicks,
        created_at=url_entry.created_at,
    )


@app.get("/api/urls", response_model=List[URLResponse], tags=["URLs"])
def list_urls(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all shortened URLs, most recent first."""
    rows = (
        db.query(URL)
        .order_by(URL.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        URLResponse(
            short_code=r.short_code,
            short_url=f"{BASE_URL}/{r.short_code}",
            original_url=r.original_url,
            clicks=r.clicks,
            created_at=r.created_at,
        )
        for r in rows
    ]


@app.get("/api/analytics/{short_code}", response_model=AnalyticsResponse, tags=["Analytics"])
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    """Get click analytics for a single short code."""
    entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found.")
    return entry


@app.get("/api/stats/summary", tags=["Analytics"])
def get_summary(db: Session = Depends(get_db)):
    """Overall stats: total links created and total clicks across all links."""
    total_urls = db.query(func.count(URL.id)).scalar() or 0
    total_clicks = db.query(func.coalesce(func.sum(URL.clicks), 0)).scalar() or 0
    return {"total_urls": total_urls, "total_clicks": total_clicks}


@app.delete("/api/urls/{short_code}", tags=["URLs"])
def delete_url(short_code: str, db: Session = Depends(get_db)):
    """Delete a shortened URL."""
    entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found.")
    db.delete(entry)
    db.commit()
    return {"detail": "deleted"}


@app.get("/{short_code}", tags=["Redirect"])
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    """Redirect a short code to its original URL and increment the click count."""
    entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found.")
    entry.clicks += 1
    entry.last_accessed = datetime.utcnow()
    db.commit()
    return RedirectResponse(url=entry.original_url, status_code=307)


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the frontend's index.html at the site root."""
    return FileResponse("static/index.html")


# Mounted under /static (NOT "/") so it can never shadow the /{short_code}
# redirect route above, e.g. GET /style.css would otherwise be swallowed by
# a catch-all mount instead of hitting the redirect handler.
app.mount("/static", StaticFiles(directory="static"), name="static")

