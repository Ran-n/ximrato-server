#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/25 10:30:44.730768
Revised: 2026/03/27 21:24:37.893749
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.lookup import (
    DistanceUnit,
    EventType,
    ExerciseCategory,
    HeightUnit,
    Language,
    MetricType,
    RpeLevel,
    Sex,
    WeightUnit,
)

_LANGUAGES = ["en", "gl", "es"]
_EVENT_TYPES = ["login", "logout", "register"]
_RPE_LEVELS = [
    "no_reps_left",
    "could_do_1",
    "could_do_2",
    "could_do_3",
    "could_do_4_5",
    "very_light",
]
_EXERCISE_CATEGORIES = ["push", "pull", "legs", "core"]
_SEXES = ["male", "female", "other"]
_WEIGHT_UNITS = ["kg", "lb"]
_DISTANCE_UNITS = ["km", "mi"]
_HEIGHT_UNITS = ["cm", "in"]
_METRIC_TYPES = ["weight", "waist", "chest", "hips", "neck", "arms", "thighs"]


def _seed_table(db: Session, model, names: list[str]) -> None:
    existing = set(db.scalars(select(model.name)).all())
    new = [model(name=n) for n in names if n not in existing]
    if new:
        db.add_all(new)
        db.commit()


def seed_all_lookup(db: Session) -> None:
    _seed_table(db, Language, _LANGUAGES)
    _seed_table(db, EventType, _EVENT_TYPES)
    _seed_table(db, RpeLevel, _RPE_LEVELS)
    _seed_table(db, ExerciseCategory, _EXERCISE_CATEGORIES)
    _seed_table(db, Sex, _SEXES)
    _seed_table(db, WeightUnit, _WEIGHT_UNITS)
    _seed_table(db, DistanceUnit, _DISTANCE_UNITS)
    _seed_table(db, HeightUnit, _HEIGHT_UNITS)
    _seed_table(db, MetricType, _METRIC_TYPES)
