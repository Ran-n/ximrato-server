#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/23 13:24:24.083385
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
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
from ximrato_server.services import storage

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


def _maybe_delete_avatar(path: str, db: Session) -> None:
    still_used = db.scalar(select(func.count(User.id)).where(User.avatar_path == path))
    if not still_used:
        storage.delete_avatar_file(path)


_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported image type"
        )
    data = await file.read()
    if len(data) > _MAX_AVATAR_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "file too large (max 5 MB)"
        )
    old_path = current_user.avatar_path
    new_path = storage.save_avatar(data)
    current_user.avatar_path = new_path
    db.commit()
    if old_path and old_path != new_path:
        _maybe_delete_avatar(old_path, db)
    log.info("upload_avatar: success user_id=%d", current_user.id)


@router.delete("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.avatar_path is None:
        return
    old_path = current_user.avatar_path
    current_user.avatar_path = None
    db.commit()
    _maybe_delete_avatar(old_path, db)
    log.info("delete_avatar: success user_id=%d", current_user.id)


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
