#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/20 13:13:46.975511
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.session import Exercise

_EXERCISES: list[tuple[str, str]] = [
    # (name, category)
    ("Bench Press", "push"),
    ("Overhead Press", "push"),
    ("Push-up", "push"),
    ("Dumbbell Fly", "push"),
    ("Tricep Dip", "push"),
    ("Tricep Pushdown", "push"),
    ("Pull-up", "pull"),
    ("Barbell Row", "pull"),
    ("Dumbbell Row", "pull"),
    ("Lat Pulldown", "pull"),
    ("Face Pull", "pull"),
    ("Barbell Curl", "pull"),
    ("Squat", "legs"),
    ("Deadlift", "legs"),
    ("Leg Press", "legs"),
    ("Lunge", "legs"),
    ("Romanian Deadlift", "legs"),
    ("Leg Curl", "legs"),
    ("Calf Raise", "legs"),
    ("Plank", "core"),
    ("Crunch", "core"),
    ("Russian Twist", "core"),
    ("Leg Raise", "core"),
    ("Ab Wheel Rollout", "core"),
]


def seed_exercises(db: Session) -> None:
    existing = set(db.scalars(select(Exercise.name)).all())
    new = [
        Exercise(name=name, category=category)
        for name, category in _EXERCISES
        if name not in existing
    ]
    if new:
        db.add_all(new)
        db.commit()
