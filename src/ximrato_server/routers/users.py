#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/20 10:41:15.687130
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.user import User, UserConfig
from ximrato_server.schemas.user import (
    UpdateUserConfigRequest,
    UpdateUserRequest,
    UserConfigResponse,
    UserResponse,
)
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
        if body.current_password is None or not auth_svc.verify_password(
            body.current_password, current_user.hashed_password
        ):
            log.warning(
                "update_me: wrong current password for user_id=%d", current_user.id
            )
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "current password is incorrect"
            )
        current_user.hashed_password = auth_svc.hash_password(body.password)
    if body.display_name is not None:
        current_user.display_name = body.display_name
    if body.sex is not None:
        current_user.sex = body.sex
    if body.date_of_birth is not None:
        current_user.date_of_birth = body.date_of_birth
    if body.height is not None:
        current_user.height = body.height
    if db.is_modified(current_user):
        db.commit()
        db.refresh(current_user)
    log.info("update_me: success user_id=%d", current_user.id)
    return current_user


def _get_or_create_config(user: User, db: Session) -> UserConfig:
    if user.config is None:
        cfg = UserConfig(user_id=user.id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
        return cfg
    return user.config


@router.get("/me/config", response_model=UserConfigResponse)
def get_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("get_config: user_id=%d", current_user.id)
    cfg = _get_or_create_config(current_user, db)
    return cfg


@router.patch("/me/config", response_model=UserConfigResponse)
def update_config(
    body: UpdateUserConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info(
        "update_config: user_id=%d fields=%r", current_user.id, body.model_fields_set
    )
    cfg = _get_or_create_config(current_user, db)
    if body.weight_unit is not None:
        cfg.weight_unit = body.weight_unit
    if body.distance_unit is not None:
        cfg.distance_unit = body.distance_unit
    if body.height_unit is not None:
        cfg.height_unit = body.height_unit
    if db.is_modified(cfg):
        db.commit()
        db.refresh(cfg)
    log.info("update_config: success user_id=%d", current_user.id)
    return cfg
