#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.860469
Revised: 2026/03/20 07:41:38.798997
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from ximrato_server import config


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "access"},
        config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=config.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": "refresh"},
        config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )


def decode_token(token: str, expected_type: str = "access") -> str:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except JWTError:
        raise ValueError("invalid token")
    if payload.get("type") != expected_type:
        raise ValueError("wrong token type")
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("missing subject")
    return sub
