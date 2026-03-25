#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.798479
Revised: 2026/03/25 12:30:29.926654
"""

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base

if TYPE_CHECKING:
    from ximrato_server.models.auth_event import AuthEvent
    from ximrato_server.models.cardio import CardioLog
    from ximrato_server.models.lookup import (
        DistanceUnit,
        HeightUnit,
        Language,
        Sex,
        WeightUnit,
    )
    from ximrato_server.models.session import WorkoutSession


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
    sex_id: Mapped[int | None] = mapped_column(ForeignKey("sexes.id"), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    avatar_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    sex_ref: Mapped["Sex | None"] = relationship("Sex")
    config: Mapped["UserConfig"] = relationship(
        "UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    sessions: Mapped[list["WorkoutSession"]] = relationship(
        "WorkoutSession", back_populates="user", cascade="all, delete-orphan"
    )
    cardio_logs: Mapped[list["CardioLog"]] = relationship(
        "CardioLog", back_populates="user", cascade="all, delete-orphan"
    )
    auth_events: Mapped[list["AuthEvent"]] = relationship(
        "AuthEvent", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def sex(self) -> str | None:
        return self.sex_ref.name if self.sex_ref else None


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

    weight_unit_id: Mapped[int] = mapped_column(ForeignKey("weight_units.id"))
    distance_unit_id: Mapped[int] = mapped_column(ForeignKey("distance_units.id"))
    height_unit_id: Mapped[int] = mapped_column(ForeignKey("height_units.id"))
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"))

    user: Mapped["User"] = relationship("User", back_populates="config")
    weight_unit_ref: Mapped["WeightUnit"] = relationship("WeightUnit")
    distance_unit_ref: Mapped["DistanceUnit"] = relationship("DistanceUnit")
    height_unit_ref: Mapped["HeightUnit"] = relationship("HeightUnit")
    language_ref: Mapped["Language"] = relationship("Language")

    @property
    def weight_unit(self) -> str:
        return self.weight_unit_ref.name

    @property
    def distance_unit(self) -> str:
        return self.distance_unit_ref.name

    @property
    def height_unit(self) -> str:
        return self.height_unit_ref.name

    @property
    def language(self) -> str:
        return self.language_ref.name
