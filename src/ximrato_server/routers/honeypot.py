#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/06 08:50:40.239133
Revised: 2026/04/06 08:51:38.678893
"""

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.orm import Session

from ximrato_server.database import get_db
from ximrato_server.security import ban_ip, get_client_ip

log = logging.getLogger("ximrato.honeypot")

router = APIRouter(tags=["honeypot"])

_ADMIN_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login \u2014 Admin</title>
  <style>
    body{font-family:sans-serif;display:flex;justify-content:center;padding-top:80px;background:#f3f4f6}
    .card{background:#fff;padding:2rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.12);width:320px}
    h2{margin-top:0;color:#111}
    label{font-size:.85rem;color:#555}
    input{width:100%;padding:.5rem;margin:.3rem 0 1rem;box-sizing:border-box;border:1px solid #d1d5db;
      border-radius:4px;font-size:.95rem}
    button{width:100%;padding:.6rem;background:#2563eb;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:.95rem}
    button:hover{background:#1d4ed8}
    .err{color:#dc2626;font-size:.85rem;margin-bottom:.8rem}
  </style>
</head>
<body>
  <div class="card">
    <h2>Admin Panel</h2>
    <form method="post" action="/admin/login">
      <label>Username</label>
      <input type="text" name="username" autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" autocomplete="current-password">
      <button type="submit">Sign in</button>
    </form>
  </div>
</body>
</html>"""

_ADMIN_HTML_INVALID = _ADMIN_HTML.replace(
    "<form",
    '<p class="err">Invalid username or password.</p>\n    <form',
)

# fake .env content — plausible-looking but entirely fictional
_FAKE_ENV = """\
APP_ENV=production
DEBUG=false
SECRET_KEY=3f8a2c1d7e4b9f0a6c5d2e1f8b3a7c4d9e2f5a8b
DATABASE_URL=postgresql://admin:Xp9mK2qLrT@localhost:5432/app_prod
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=7b1e4c9d2f5a8b3e6c1d4f7a2b5e8c3d1f6a9b2e
"""


def _ban(request: Request, db: Session) -> None:
    ip = get_client_ip(request)
    log.warning("honeypot hit ip=%r path=%r method=%r", ip, request.url.path, request.method)
    ban_ip(ip, f"honeypot:{request.url.path}", db)


@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/login", response_class=HTMLResponse)
@router.get("/wp-admin", response_class=HTMLResponse)
@router.get("/wp-admin/", response_class=HTMLResponse)
@router.get("/phpmyadmin", response_class=HTMLResponse)
async def honeypot_admin(request: Request, db: Session = Depends(get_db)):
    _ban(request, db)
    return HTMLResponse(_ADMIN_HTML)


@router.post("/admin/login", response_class=HTMLResponse)
@router.post("/wp-admin/wp-login.php", response_class=HTMLResponse)
async def honeypot_login(request: Request, db: Session = Depends(get_db)):
    _ban(request, db)
    return HTMLResponse(_ADMIN_HTML_INVALID)


@router.get("/.env", response_class=PlainTextResponse)
@router.get("/config.php", response_class=PlainTextResponse)
@router.get("/.git/config", response_class=PlainTextResponse)
async def honeypot_env(request: Request, db: Session = Depends(get_db)):
    _ban(request, db)
    return PlainTextResponse(_FAKE_ENV)
