#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 18:00:00.000000
Revised: 2026/03/24 18:02:47.279932
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.cardio import CardioExercise

_CARDIO_EXERCISES: list[tuple[str, str, str]] = [
    # (name, name_es, name_gl)
    ("Running", "Carrera", "Carreira"),
    ("Cycling", "Ciclismo", "Ciclismo"),
    ("Rowing", "Remo", "Remo"),
]


def seed_cardio_exercises(db: Session) -> None:
    existing_map: dict[str, CardioExercise] = {ex.name: ex for ex in db.scalars(select(CardioExercise)).all()}

    for name, name_es, name_gl in _CARDIO_EXERCISES:
        ex = existing_map.get(name)
        if ex is None:
            ex = CardioExercise(name=name)
            db.add(ex)
        ex.name_es = name_es
        ex.name_gl = name_gl

    db.commit()
