#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:38:31.844790
Revised: 2026/03/23 11:57:36.240386
"""

import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ximrato.db")
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "static")
BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")
