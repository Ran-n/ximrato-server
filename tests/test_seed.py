#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:25:00.000000
Revised: 2026/03/20 13:25:00.000000
"""

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from ximrato_server.database import Base
from ximrato_server.models.session import Exercise
from ximrato_server.seed.exercises import _EXERCISES, seed_exercises


def _fresh_db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    return engine


def test_seed_inserts_all_exercises():
    engine = _fresh_db()
    with Session(engine) as db:
        seed_exercises(db)
        count = db.scalar(select(func.count()).select_from(Exercise))
    assert count == len(_EXERCISES)


def test_seed_is_idempotent():
    engine = _fresh_db()
    with Session(engine) as db:
        seed_exercises(db)
        seed_exercises(db)
        count = db.scalar(select(func.count()).select_from(Exercise))
    assert count == len(_EXERCISES)


def test_seed_inserts_only_missing():
    engine = _fresh_db()
    with Session(engine) as db:
        db.add(Exercise(name=_EXERCISES[0][0], category=_EXERCISES[0][1]))
        db.commit()
        seed_exercises(db)
        count = db.scalar(select(func.count()).select_from(Exercise))
    assert count == len(_EXERCISES)


def test_seed_sets_correct_categories():
    engine = _fresh_db()
    with Session(engine) as db:
        seed_exercises(db)
        exercises = db.scalars(select(Exercise)).all()
    names_to_cat = {e.name: e.category for e in exercises}
    assert names_to_cat["Bench Press"] == "push"
    assert names_to_cat["Pull-up"] == "pull"
    assert names_to_cat["Squat"] == "legs"
    assert names_to_cat["Plank"] == "core"
