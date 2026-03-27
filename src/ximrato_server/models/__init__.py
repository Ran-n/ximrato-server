#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/25 07:33:53.806180
Revised: 2026/03/27 21:24:37.451349
"""

# Import all models here so SQLAlchemy's mapper registry has every class
# registered before any relationship string-reference is resolved.
from ximrato_server.models.auth_event import AuthEvent  # noqa: F401
from ximrato_server.models.body_metric import BodyMetric  # noqa: F401
from ximrato_server.models.cardio import CardioExercise, CardioLog  # noqa: F401
from ximrato_server.models.lookup import (  # noqa: F401
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
from ximrato_server.models.session import WorkoutSession, WorkoutSet  # noqa: F401
from ximrato_server.models.user import User, UserConfig  # noqa: F401
