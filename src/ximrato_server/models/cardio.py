#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/24 18:00:00.000000
Revised: 2026/03/24 18:02:47.007762
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base

if TYPE_CHECKING:
    from ximrato_server.models.user import User


class CardioExercise(Base):
    __tablename__ = "cardio_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    logs: Mapped[list["CardioLog"]] = relationship(
        "CardioLog", back_populates="exercise"
    )


class CardioLog(Base):
    __tablename__ = "cardio_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("cardio_exercises.id"), index=True
    )
    duration_seconds: Mapped[int] = mapped_column(Integer)
    distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elevation_gain: Mapped[float | None] = mapped_column(Float, nullable=True)
    stroke_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="cardio_logs")
    exercise: Mapped["CardioExercise"] = relationship(
        "CardioExercise", back_populates="logs"
    )
