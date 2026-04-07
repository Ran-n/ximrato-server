#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/06 08:50:40.144047
Revised: 2026/04/07 08:29:36.606796
"""

import logging
import re

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

log = logging.getLogger("ximrato.security")

# in-memory set of banned IPs — populated from DB at startup, updated on every new ban
BANNED_IPS: set[str] = set()

# known scanner / attack-tool User-Agent substrings (case-insensitive)
# only include tools with no legitimate user use-case — do NOT add generic HTTP
# clients (curl, httpx, requests, axios, wget, java, okhttp) as they are used
# by real apps and developers
_SCANNER_UA_RE = re.compile(
    r"masscan|zgrab|nmap|nikto|sqlmap|dirbuster|gobuster|feroxbuster|"
    r"wfuzz|hydra|nuclei|acunetix|nessus|openvas|burpsuite|zaproxy",
    re.IGNORECASE,
)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def is_scanner_ua(user_agent: str) -> bool:
    return bool(_SCANNER_UA_RE.search(user_agent))


def ban_ip(ip: str, reason: str, db: Session) -> None:
    from ximrato_server.models.banned_ip import BannedIP

    BANNED_IPS.add(ip)
    existing = db.scalar(select(BannedIP).where(BannedIP.ip == ip))
    if not existing:
        db.add(BannedIP(ip=ip, reason=reason))
        db.commit()
    log.warning("banned ip=%r reason=%r", ip, reason)
