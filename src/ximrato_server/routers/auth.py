#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.987006
Revised: 2026/03/25 10:48:26.380063
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.auth_event import AuthEvent
from ximrato_server.models.lookup import EventType
from ximrato_server.models.user import User
from ximrato_server.schemas.auth import (
    AuthEventOut,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from ximrato_server.services import auth as auth_svc

log = logging.getLogger("ximrato.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


def _event_type_id(db: Session, name: str) -> int:
    row = db.scalar(select(EventType).where(EventType.name == name))
    if row is None:
        raise RuntimeError(f"event type not seeded: {name!r}")
    return row.id


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    log.info("register attempt: username=%r email=%r", body.username, body.email)
    if db.scalar(select(User).where(User.username == body.username)):
        log.warning("register failed: username already taken: %r", body.username)
        raise HTTPException(status.HTTP_409_CONFLICT, "username already taken")
    if db.scalar(select(User).where(User.email == body.email)):
        log.warning("register failed: email already registered: %r", body.email)
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=auth_svc.hash_password(body.password),
    )
    db.add(user)
    db.flush()
    db.add(AuthEvent(user_id=user.id, event_type_id=_event_type_id(db, "register")))
    db.commit()
    log.info("register success: user_id=%d username=%r", user.id, user.username)
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    log.info("login attempt: username=%r", body.username)
    user = db.scalar(select(User).where(User.username == body.username))
    if not user or not auth_svc.verify_password(body.password, user.hashed_password):
        log.warning("login failed: invalid credentials for username=%r", body.username)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    db.add(AuthEvent(user_id=user.id, event_type_id=_event_type_id(db, "login")))
    db.commit()
    log.info("login success: user_id=%d username=%r", user.id, user.username)
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.add(
        AuthEvent(user_id=current_user.id, event_type_id=_event_type_id(db, "logout"))
    )
    db.commit()
    log.info("logout: user_id=%d username=%r", current_user.id, current_user.username)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    log.info("token refresh attempt")
    try:
        user_id = auth_svc.decode_token(body.refresh_token, expected_type="refresh")
    except ValueError as exc:
        log.warning("token refresh failed: %s", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    user = db.get(User, int(user_id))
    if not user:
        log.warning("token refresh failed: user_id=%s not found", user_id)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    log.info("token refresh success: user_id=%d username=%r", user.id, user.username)
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )


@router.get("/events", response_model=list[AuthEventOut])
def list_events(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    rows = db.scalars(
        select(AuthEvent)
        .where(AuthEvent.user_id == current_user.id)
        .order_by(AuthEvent.occurred_at.desc())
        .options(selectinload(AuthEvent.event_type))
    ).all()
    return rows
