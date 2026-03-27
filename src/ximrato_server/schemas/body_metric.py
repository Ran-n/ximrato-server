#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/27 00:00:00.000000
Revised: 2026/03/27 20:18:20.872868
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

MetricType = Literal["weight", "waist", "chest", "hips", "neck", "arms", "thighs"]


class CreateBodyMetricRequest(BaseModel):
    metric_type: MetricType
    value: float


class BodyMetricResponse(BaseModel):
    id: int
    logged_at: datetime
    metric_type: str
    value: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
