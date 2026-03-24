#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/23 11:57:52.568898
Revised: 2026/03/23 13:24:24.000955
"""

import io
from pathlib import Path

import blake3
from PIL import Image

from ximrato_server import config

_UPLOAD_DIR = Path(config.UPLOAD_DIR)
_AVATAR_DIR = _UPLOAD_DIR / "avatars"
_MAX_DIM = 128


def delete_avatar_file(rel_path: str) -> None:
    """Delete an avatar file from disk; no-op if it does not exist."""
    dest = _UPLOAD_DIR / rel_path
    if dest.exists():
        dest.unlink()


def save_avatar(data: bytes) -> str:
    """Resize to at most 128×128 WebP, persist under BLAKE3 content hash."""
    _AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.open(io.BytesIO(data))
    if img.mode == "P":
        img = img.convert("RGBA")
    img.thumbnail((_MAX_DIM, _MAX_DIM), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=85)
    webp_bytes = buf.getvalue()
    digest = blake3.blake3(webp_bytes).hexdigest()
    rel_path = f"avatars/{digest}.webp"
    dest = _UPLOAD_DIR / rel_path
    if not dest.exists():
        dest.write_bytes(webp_bytes)
    return rel_path
