#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.987006
Revised: 2026/03/20 07:39:09.987006
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.database import get_db
from ximrato_server.models.user import User
from ximrato_server.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from ximrato_server.services import auth as auth_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == body.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "username already taken")
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=auth_svc.hash_password(body.password),
    )
    db.add(user)
    db.commit()
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    if not user or not auth_svc.verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        user_id = auth_svc.decode_token(body.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return TokenResponse(
        access_token=auth_svc.create_access_token(str(user.id)),
        refresh_token=auth_svc.create_refresh_token(str(user.id)),
    )
