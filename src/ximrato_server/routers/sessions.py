#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/27 21:24:37.695570
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.lookup import RpeLevel
from ximrato_server.models.session import Exercise, WorkoutSession, WorkoutSet
from ximrato_server.models.user import User
from ximrato_server.schemas.session import (
    AddSetRequest,
    EndSessionRequest,
    WorkoutSessionResponse,
    WorkoutSetResponse,
)

log = logging.getLogger("ximrato.sessions")

router = APIRouter(prefix="/sessions", tags=["sessions"])

_SESSION_LOAD = [
    selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise).selectinload(Exercise.category_ref),
    selectinload(WorkoutSession.sets).selectinload(WorkoutSet.rpe_level),
]


def _get_session_or_404(session_id: int, user: User, db: Session) -> WorkoutSession:
    ws = db.scalar(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user.id)
        .options(*_SESSION_LOAD)
    )
    if not ws:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")
    return ws


@router.get("/active", response_model=WorkoutSessionResponse | None)
def get_active(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("get_active: user_id=%d", current_user.id)
    return db.scalar(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.ended_at.is_(None),
        )
        .options(*_SESSION_LOAD)
    )


@router.get("", response_model=list[WorkoutSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("list_sessions: user_id=%d", current_user.id)
    return db.scalars(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.ended_at.is_not(None),
        )
        .order_by(WorkoutSession.started_at.desc())
        .options(*_SESSION_LOAD)
    ).all()


@router.post("", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("start_session: user_id=%d", current_user.id)
    active = db.scalar(
        select(WorkoutSession).where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.ended_at.is_(None),
        )
    )
    if active:
        raise HTTPException(status.HTTP_409_CONFLICT, "session already active")
    ws = WorkoutSession(user_id=current_user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    log.info("start_session: session_id=%d", ws.id)
    return db.scalar(select(WorkoutSession).where(WorkoutSession.id == ws.id).options(*_SESSION_LOAD))


@router.patch("/{session_id}/end", response_model=WorkoutSessionResponse)
def end_session(
    session_id: int,
    body: EndSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("end_session: user_id=%d session_id=%d", current_user.id, session_id)
    ws = _get_session_or_404(session_id, current_user, db)
    if ws.ended_at is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "session already ended")
    ws.ended_at = datetime.now(timezone.utc)
    if body.notes is not None:
        ws.notes = body.notes
    db.commit()
    db.refresh(ws)
    return ws


@router.post(
    "/{session_id}/sets",
    response_model=WorkoutSetResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_set(
    session_id: int,
    body: AddSetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info(
        "add_set: user_id=%d session_id=%d exercise_id=%d",
        current_user.id,
        session_id,
        body.exercise_id,
    )
    ws = _get_session_or_404(session_id, current_user, db)
    if ws.ended_at is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "session already ended")
    exercise = db.get(Exercise, body.exercise_id)
    if not exercise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise not found")

    rpe_level_id: int | None = None
    if body.rpe is not None:
        row = db.scalar(select(RpeLevel).where(RpeLevel.name == body.rpe.value))
        if row is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "unknown rpe")
        rpe_level_id = row.id

    wset = WorkoutSet(
        session_id=ws.id,
        exercise_id=body.exercise_id,
        reps=body.reps,
        weight=body.weight,
        bodyweight_counted=body.bodyweight_counted,
        rpe_level_id=rpe_level_id,
        to_failure=body.to_failure,
    )
    db.add(wset)
    db.commit()
    db.refresh(wset)
    return db.scalar(
        select(WorkoutSet)
        .where(WorkoutSet.id == wset.id)
        .options(
            selectinload(WorkoutSet.exercise).selectinload(Exercise.category_ref),
            selectinload(WorkoutSet.rpe_level),
        )
    )
