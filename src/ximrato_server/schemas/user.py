#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 09:03:49.000000
Revised: 2026/03/20 09:49:18.009472
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
