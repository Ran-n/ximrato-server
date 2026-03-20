#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.732979
Revised: 2026/03/20 07:39:09.732979
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from ximrato_server.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


class Base(DeclarativeBase):
    pass


def get_db():
    with Session(engine) as session:
        yield session
