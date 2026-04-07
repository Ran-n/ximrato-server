#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 08:51:55.122400
Revised: 2026/04/06 14:09:08.746985
"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session as DbSession

from ximrato_server import config, models  # noqa: F401 — registers all ORM models
from ximrato_server.database import Base, engine, get_db
from ximrato_server.models.banned_ip import BannedIP
from ximrato_server.routers import auth, body_metrics, cardio, exercises, health, honeypot, sessions, users
from ximrato_server.security import BANNED_IPS, ban_ip, get_client_ip, is_scanner_ua
from ximrato_server.seed import seed_all_lookup, seed_cardio_exercises, seed_exercises

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ximrato")


def _apply_schema_patches() -> None:
    """Add new columns to existing tables if absent — safe to run on any DB."""
    inspector = inspect(engine)

    def _add_if_missing(table: str, col: str, ddl: str) -> None:
        cols = {c["name"] for c in inspector.get_columns(table)}
        if col not in cols:
            with engine.connect() as conn:
                conn.execute(text(ddl))
                conn.commit()

    _patches = [
        ("exercises", "equipment_type", "ALTER TABLE exercises ADD COLUMN equipment_type VARCHAR(32)"),
        ("exercises", "primary_muscles", "ALTER TABLE exercises ADD COLUMN primary_muscles TEXT"),
        ("exercises", "secondary_muscles", "ALTER TABLE exercises ADD COLUMN secondary_muscles TEXT"),
        ("exercises", "description", "ALTER TABLE exercises ADD COLUMN description VARCHAR(512)"),
        ("exercises", "name_es", "ALTER TABLE exercises ADD COLUMN name_es VARCHAR(128)"),
        ("exercises", "name_gl", "ALTER TABLE exercises ADD COLUMN name_gl VARCHAR(128)"),
        ("cardio_exercises", "name_es", "ALTER TABLE cardio_exercises ADD COLUMN name_es VARCHAR(128)"),
        ("cardio_exercises", "name_gl", "ALTER TABLE cardio_exercises ADD COLUMN name_gl VARCHAR(128)"),
    ]
    for table, col, ddl in _patches:
        _add_if_missing(table, col, ddl)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _apply_schema_patches()
    with DbSession(engine) as db:
        seed_all_lookup(db)
        seed_exercises(db)
        seed_cardio_exercises(db)
    Path(config.UPLOAD_DIR).mkdir(exist_ok=True)
    with DbSession(engine) as db:
        banned = db.scalars(select(BannedIP)).all()
        BANNED_IPS.update(b.ip for b in banned)
    log.info("loaded %d banned ip(s)", len(BANNED_IPS))
    yield
    engine.dispose()
    log.info("database engine disposed")


app = FastAPI(title="ximrato-server", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=config.UPLOAD_DIR), name="static")
app.include_router(health.router)
app.include_router(honeypot.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(sessions.router)
app.include_router(cardio.router)
app.include_router(body_metrics.router)


@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    log.info(
        "%s %s → %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        ms,
    )
    return response


@app.middleware("http")
async def ip_ban(request: Request, call_next):
    ip = get_client_ip(request)
    if ip in BANNED_IPS:
        log.info("blocked %s %s from banned ip=%r", request.method, request.url.path, ip)
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    ua = request.headers.get("User-Agent", "")
    if ua and is_scanner_ua(ua):
        db_factory = request.app.dependency_overrides.get(get_db, get_db)
        db = next(db_factory())
        ban_ip(ip, f"scanner-ua:{ua[:80]}", db)
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for err in errors:
        field = " → ".join(str(p) for p in err.get("loc", []) if p != "body")
        log.warning(
            "422 %s %s — field=%r msg=%r",
            request.method,
            request.url.path,
            field,
            err.get("msg"),
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": errors},
    )
