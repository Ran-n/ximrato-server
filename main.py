#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:10.111263
Revised: 2026/03/20 13:13:49.685157
"""

import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DbSession

from ximrato_server.database import Base, engine
from ximrato_server.routers import auth, exercises, health, sessions, users
from ximrato_server.seed import seed_exercises

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ximrato")

Base.metadata.create_all(bind=engine)

with DbSession(engine) as db:
    seed_exercises(db)

app = FastAPI(title="ximrato-server")
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(sessions.router)


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
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )
