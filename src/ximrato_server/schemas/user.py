#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/25 10:48:26.959279
"""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, computed_field

from ximrato_server import config
from ximrato_server.schemas.enums import (
    DistanceUnitEnum,
    HeightUnitEnum,
    SexEnum,
    WeightUnitEnum,
)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None
    sex: SexEnum | None
    date_of_birth: date | None
    height: float | None
    avatar_path: str | None = Field(None, exclude=True)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def avatar_url(self) -> str | None:
        if self.avatar_path is None:
            return None
        return f"{config.BASE_URL}/static/{self.avatar_path}"

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    current_password: str | None = None
    password: str | None = None
    display_name: str | None = None
    sex: SexEnum | None = None
    date_of_birth: date | None = None
    height: float | None = None


class UserConfigResponse(BaseModel):
    weight_unit: WeightUnitEnum
    distance_unit: DistanceUnitEnum
    height_unit: HeightUnitEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserConfigRequest(BaseModel):
    weight_unit: WeightUnitEnum | None = None
    distance_unit: DistanceUnitEnum | None = None
    height_unit: HeightUnitEnum | None = None
