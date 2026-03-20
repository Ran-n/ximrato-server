#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/20 12:02:43.139275
"""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr

from ximrato_server.models.user import DistanceUnit, HeightUnit, Sex, WeightUnit


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None
    sex: Sex | None
    date_of_birth: date | None
    height: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    current_password: str | None = None
    password: str | None = None
    display_name: str | None = None
    sex: Sex | None = None
    date_of_birth: date | None = None
    height: float | None = None


class UserConfigResponse(BaseModel):
    weight_unit: WeightUnit
    distance_unit: DistanceUnit
    height_unit: HeightUnit
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserConfigRequest(BaseModel):
    weight_unit: WeightUnit | None = None
    distance_unit: DistanceUnit | None = None
    height_unit: HeightUnit | None = None
