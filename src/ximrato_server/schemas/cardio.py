#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 18:00:00.000000
Revised: 2026/03/24 18:02:47.197935
"""

from datetime import datetime

from pydantic import BaseModel


class CardioExerciseResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CreateCardioLogRequest(BaseModel):
    exercise_id: int
    duration_seconds: int
    distance: float | None = None
    avg_heart_rate: int | None = None
    elevation_gain: float | None = None
    stroke_rate: int | None = None


class CardioLogResponse(BaseModel):
    id: int
    exercise: CardioExerciseResponse
    duration_seconds: int
    distance: float | None
    logged_at: datetime
    rest_seconds: int | None
    avg_heart_rate: int | None
    elevation_gain: float | None
    stroke_rate: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
