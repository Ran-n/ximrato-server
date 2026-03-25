#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 18:00:00.000000
Revised: 2026/03/24 18:02:47.444080
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.cardio import CardioExercise, CardioLog
from ximrato_server.models.user import User
from ximrato_server.schemas.cardio import (
    CardioExerciseResponse,
    CardioLogResponse,
    CreateCardioLogRequest,
)

log = logging.getLogger("ximrato.cardio")

router = APIRouter(prefix="/cardio", tags=["cardio"])

_LOG_LOAD = [selectinload(CardioLog.exercise)]


@router.get("/exercises", response_model=list[CardioExerciseResponse])
def list_cardio_exercises(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    log.info("list_cardio_exercises")
    return db.scalars(select(CardioExercise).order_by(CardioExercise.name)).all()


@router.post("", response_model=CardioLogResponse, status_code=status.HTTP_201_CREATED)
def create_cardio_log(
    body: CreateCardioLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info(
        "create_cardio_log: user_id=%d exercise_id=%d",
        current_user.id,
        body.exercise_id,
    )
    clog = CardioLog(
        user_id=current_user.id,
        exercise_id=body.exercise_id,
        duration_seconds=body.duration_seconds,
        distance=body.distance,
        avg_heart_rate=body.avg_heart_rate,
        elevation_gain=body.elevation_gain,
        stroke_rate=body.stroke_rate,
    )
    db.add(clog)
    db.commit()
    db.refresh(clog)
    log.info("create_cardio_log: id=%d", clog.id)
    return db.scalar(
        select(CardioLog).where(CardioLog.id == clog.id).options(*_LOG_LOAD)
    )


@router.get("", response_model=list[CardioLogResponse])
def list_cardio_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("list_cardio_logs: user_id=%d", current_user.id)
    return db.scalars(
        select(CardioLog)
        .where(CardioLog.user_id == current_user.id)
        .order_by(CardioLog.logged_at.desc())
        .options(*_LOG_LOAD)
    ).all()
