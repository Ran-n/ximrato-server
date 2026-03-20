#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:10.111263
Revised: 2026/03/20 07:39:10.111263
"""

from fastapi import FastAPI

from ximrato_server.database import Base, engine
from ximrato_server.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ximrato-server")
app.include_router(auth.router)
