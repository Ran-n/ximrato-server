#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/27 00:00:00.000000
Revised: 2026/03/27 20:24:46.831421
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ximrato_server.database import Base

if TYPE_CHECKING:
    from ximrato_server.models.lookup import MetricType
    from ximrato_server.models.user import User


class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metric_type_id: Mapped[int] = mapped_column(ForeignKey("metric_types.id"), index=True)
    value: Mapped[float] = mapped_column(Float)

    user: Mapped["User"] = relationship("User", back_populates="body_metrics")
    metric_type_rel: Mapped["MetricType"] = relationship("MetricType")

    @property
    def metric_type(self) -> str:
        return self.metric_type_rel.name
