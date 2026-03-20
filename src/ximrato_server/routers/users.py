#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/20 09:49:18.150446
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.user import User
from ximrato_server.schemas.user import UpdateUserRequest, UserResponse
from ximrato_server.services import auth as auth_svc

log = logging.getLogger("ximrato.users")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    log.info("get_me: user_id=%d username=%r", current_user.id, current_user.username)
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    body: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("update_me: user_id=%d fields=%r", current_user.id, body.model_fields_set)
    if body.username is not None and body.username != current_user.username:
        if db.scalar(select(User).where(User.username == body.username)):
            log.warning("update_me: username already taken: %r", body.username)
            raise HTTPException(status.HTTP_409_CONFLICT, "username already taken")
        current_user.username = body.username
    if body.email is not None and body.email != current_user.email:
        if db.scalar(select(User).where(User.email == body.email)):
            log.warning("update_me: email already registered: %r", body.email)
            raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
        current_user.email = body.email
    if body.password is not None:
        current_user.hashed_password = auth_svc.hash_password(body.password)
    db.commit()
    db.refresh(current_user)
    log.info("update_me: success user_id=%d", current_user.id)
    return current_user
