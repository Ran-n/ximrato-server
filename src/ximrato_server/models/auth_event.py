#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/25 10:20:00.000000
Revised: 2026/03/25 10:48:30.040657
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base

if TYPE_CHECKING:
    from ximrato_server.models.lookup import EventType
    from ximrato_server.models.user import User


class AuthEvent(Base):
    __tablename__ = "auth_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"), index=True)

    user: Mapped["User"] = relationship("User", back_populates="auth_events")
    event_type: Mapped["EventType"] = relationship("EventType")

    @property
    def event(self) -> str:
        return self.event_type.name
