#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:09.987006
Revised: 2026/03/20 09:41:23.509940
"""

import logging

from fastapi import APIRouter

log = logging.getLogger("ximrato.health")

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
def root() -> dict:
    log.debug("health check")
    return {"status": "ok", "service": "ximrato-server"}
