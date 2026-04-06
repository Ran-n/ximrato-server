#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/06 08:50:40.065976
Revised: 2026/04/06 08:50:40.065976
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ximrato_server.database import Base


class BannedIP(Base):
    __tablename__ = "banned_ips"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(String(45), unique=True, index=True)
    reason: Mapped[str] = mapped_column(String(256), default="honeypot")
    banned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
