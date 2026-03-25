#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 18:00:00.000000
Revised: 2026/03/24 18:02:47.279932
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.cardio import CardioExercise

_CARDIO_EXERCISES: list[str] = ["Running", "Cycling", "Rowing"]


def seed_cardio_exercises(db: Session) -> None:
    existing = set(db.scalars(select(CardioExercise.name)).all())
    new = [
        CardioExercise(name=name) for name in _CARDIO_EXERCISES if name not in existing
    ]
    if new:
        db.add_all(new)
        db.commit()
