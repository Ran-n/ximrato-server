#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.798479
Revised: 2026/03/20 12:02:43.067043
"""

import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base


class Sex(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class WeightUnit(str, enum.Enum):
    kg = "kg"
    lb = "lb"


class DistanceUnit(str, enum.Enum):
    km = "km"
    mi = "mi"


class HeightUnit(str, enum.Enum):
    cm = "cm"
    inch = "in"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256))

    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sex: Mapped[Sex | None] = mapped_column(Enum(Sex), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)

    config: Mapped["UserConfig"] = relationship(
        "UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserConfig(Base):
    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )

    weight_unit: Mapped[WeightUnit] = mapped_column(
        Enum(WeightUnit), default=WeightUnit.kg, server_default=WeightUnit.kg.value
    )
    distance_unit: Mapped[DistanceUnit] = mapped_column(
        Enum(DistanceUnit),
        default=DistanceUnit.km,
        server_default=DistanceUnit.km.value,
    )
    height_unit: Mapped[HeightUnit] = mapped_column(
        Enum(HeightUnit), default=HeightUnit.cm, server_default=HeightUnit.cm.value
    )

    user: Mapped["User"] = relationship("User", back_populates="config")
