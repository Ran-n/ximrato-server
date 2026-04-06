#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/04/01 07:41:51.828327
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.lookup import ExerciseCategory
from ximrato_server.models.session import Exercise, WorkoutSession, WorkoutSet
from ximrato_server.models.user import User
from ximrato_server.schemas.session import ExerciseProgressPoint, ExerciseResponse

log = logging.getLogger("ximrato.exercises")

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseResponse])
def list_exercises(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    log.info("list_exercises")
    return db.scalars(
        select(Exercise)
        .join(Exercise.category_ref, isouter=True)
        .order_by(ExerciseCategory.name, Exercise.name)
        .options(selectinload(Exercise.category_ref))
    ).all()


@router.get("/{exercise_id}/progress", response_model=list[ExerciseProgressPoint])
def get_exercise_progress(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("get_exercise_progress: exercise_id=%d user_id=%d", exercise_id, current_user.id)
    rows = db.execute(
        select(
            func.date(WorkoutSession.ended_at).label("date"),
            func.max(WorkoutSet.weight).label("max_weight"),
            func.max(WorkoutSet.reps).label("max_reps"),
            func.sum(WorkoutSet.weight * WorkoutSet.reps).label("total_volume"),
        )
        .join(WorkoutSession, WorkoutSet.session_id == WorkoutSession.id)
        .where(
            WorkoutSet.exercise_id == exercise_id,
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.ended_at.is_not(None),
        )
        .group_by(func.date(WorkoutSession.ended_at))
        .order_by(func.date(WorkoutSession.ended_at))
    ).all()

    return [
        ExerciseProgressPoint(
            date=str(row.date),
            max_weight=row.max_weight or 0.0,
            max_reps=int(row.max_reps or 0),
            total_volume=row.total_volume or 0.0,
        )
        for row in rows
    ]
