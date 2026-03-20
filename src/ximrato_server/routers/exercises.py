#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/20 13:13:49.555364
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.session import Exercise
from ximrato_server.models.user import User
from ximrato_server.schemas.session import ExerciseResponse

log = logging.getLogger("ximrato.exercises")

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseResponse])
def list_exercises(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    log.info("list_exercises")
    return db.scalars(select(Exercise).order_by(Exercise.category, Exercise.name)).all()
