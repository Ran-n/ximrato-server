#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/25 10:48:26.218917
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base

if TYPE_CHECKING:
    from ximrato_server.models.lookup import ExerciseCategory, RpeLevel
    from ximrato_server.models.user import User


class Exercise(Base):
    __tablename__ = "exercises"

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
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercise_categories.id"), nullable=True
    )

    category_ref: Mapped["ExerciseCategory | None"] = relationship("ExerciseCategory")
    sets: Mapped[list["WorkoutSet"]] = relationship(
        "WorkoutSet", back_populates="exercise"
    )

    @property
    def category(self) -> str | None:
        return self.category_ref.name if self.category_ref else None


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

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
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    sets: Mapped[list["WorkoutSet"]] = relationship(
        "WorkoutSet",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.logged_at",
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    bodyweight_counted: Mapped[bool] = mapped_column(Boolean, default=False)
    rpe_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("rpe_levels.id"), nullable=True
    )
    to_failure: Mapped[bool] = mapped_column(Boolean, default=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["WorkoutSession"] = relationship(
        "WorkoutSession", back_populates="sets"
    )
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="sets")
    rpe_level: Mapped["RpeLevel | None"] = relationship("RpeLevel")

    @property
    def rpe(self) -> str | None:
        return self.rpe_level.name if self.rpe_level else None
