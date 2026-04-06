#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/25 10:48:26.867481
"""

from datetime import datetime

from pydantic import BaseModel

from ximrato_server.schemas.enums import RPEEnum


class ExerciseResponse(BaseModel):
    id: int
    name: str
    category: str | None
    equipment_type: str | None = None
    primary_muscles: list[str] | None = None
    secondary_muscles: list[str] | None = None
    description: str | None = None
    name_es: str | None = None
    name_gl: str | None = None

    model_config = {"from_attributes": True}


class WorkoutSetResponse(BaseModel):
    id: int
    exercise: ExerciseResponse
    reps: int
    weight: float
    bodyweight_counted: bool
    rpe: RPEEnum | None
    to_failure: bool
    logged_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSessionResponse(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime | None
    notes: str | None
    sets: list[WorkoutSetResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EndSessionRequest(BaseModel):
    notes: str | None = None


class AddSetRequest(BaseModel):
    exercise_id: int
    reps: int
    weight: float
    bodyweight_counted: bool = False
    rpe: RPEEnum | None = None
    to_failure: bool = False


class ExerciseProgressPoint(BaseModel):
    date: str
    max_weight: float
    max_reps: int
    total_volume: float
