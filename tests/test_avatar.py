#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/23 12:11:35.201747
Revised: 2026/03/23 13:27:36.532168
"""

import io

from PIL import Image

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _jpeg(size=(10, 10)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=(100, 150, 200)).save(buf, "JPEG")
    return buf.getvalue()


def _register(client, username, email="u@example.com", password="pass1234"):
    r = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code == 201
    return r.json()


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# POST /users/me/avatar
# ---------------------------------------------------------------------------


def test_upload_avatar_ok(client, monkeypatch, tmp_path):
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avup1", "avup1@example.com")
    r = client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 204


def test_avatar_url_in_get_me(client, monkeypatch, tmp_path):
    import ximrato_server.config as cfg
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(cfg, "BASE_URL", "http://testserver")
    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avurl1", "avurl1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
        headers=headers,
    )
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200
    url = r.json()["avatar_url"]
    assert url is not None
    assert url.startswith("http://testserver/static/avatars/")


def test_no_avatar_url_is_none(client):
    tokens = _register(client, "noav1", "noav1@example.com")
    r = client.get("/users/me", headers=_auth_header(tokens["access_token"]))
    assert r.json()["avatar_url"] is None


def test_upload_avatar_invalid_type(client):
    tokens = _register(client, "avbad1", "avbad1@example.com")
    r = client.post(
        "/users/me/avatar",
        files={"file": ("file.txt", b"hello world", "text/plain")},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 415


def test_upload_avatar_too_large(client, monkeypatch):
    import ximrato_server.routers.users as users_router

    monkeypatch.setattr(users_router, "_MAX_AVATAR_BYTES", 1)
    tokens = _register(client, "avbig1", "avbig1@example.com")
    r = client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 413


def test_upload_avatar_unauthenticated(client):
    r = client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
    )
    assert r.status_code in {401, 403}


# ---------------------------------------------------------------------------
# DELETE /users/me/avatar
# ---------------------------------------------------------------------------


def test_delete_avatar_ok(client, monkeypatch, tmp_path):
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avdel1", "avdel1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
        headers=headers,
    )
    r = client.delete("/users/me/avatar", headers=headers)
    assert r.status_code == 204


def test_delete_avatar_clears_url(client, monkeypatch, tmp_path):
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avclr1", "avclr1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg(), "image/jpeg")},
        headers=headers,
    )
    client.delete("/users/me/avatar", headers=headers)
    r = client.get("/users/me", headers=headers)
    assert r.json()["avatar_url"] is None


def test_delete_avatar_no_avatar_is_noop(client):
    tokens = _register(client, "avnoop1", "avnoop1@example.com")
    r = client.delete("/users/me/avatar", headers=_auth_header(tokens["access_token"]))
    assert r.status_code == 204


def test_upload_replaces_existing(client, monkeypatch, tmp_path):
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avrep1", "avrep1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("a.jpg", _jpeg(), "image/jpeg")},
        headers=headers,
    )
    r = client.post(
        "/users/me/avatar",
        files={"file": ("b.jpg", _jpeg(), "image/jpeg")},
        headers=headers,
    )
    assert r.status_code == 204


def test_upload_file_is_resized(client, monkeypatch, tmp_path):
    """Uploaded images must be resized to at most 128×128."""
    import ximrato_server.config as cfg
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(cfg, "BASE_URL", "http://testserver")
    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    tokens = _register(client, "avresize1", "avresize1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("big.jpg", _jpeg((512, 512)), "image/jpeg")},
        headers=headers,
    )
    url = client.get("/users/me", headers=headers).json()["avatar_url"]
    filename = url.split("/")[-1]
    saved = Image.open(tmp_path / "avatars" / filename)
    assert saved.width <= 128
    assert saved.height <= 128


def test_same_content_reuses_file(client, monkeypatch, tmp_path):
    """Two users uploading identical bytes share one file on disk."""
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")

    img_bytes = _jpeg()
    tokens_a = _register(client, "avdedup1", "avdedup1@example.com")
    tokens_b = _register(client, "avdedup2", "avdedup2@example.com")
    for tokens in (tokens_a, tokens_b):
        client.post(
            "/users/me/avatar",
            files={"file": ("avatar.jpg", img_bytes, "image/jpeg")},
            headers=_auth_header(tokens["access_token"]),
        )
    assert len(list((tmp_path / "avatars").iterdir())) == 1


def test_delete_avatar_unauthenticated(client):
    r = client.delete("/users/me/avatar")
    assert r.status_code in {401, 403}


# ---------------------------------------------------------------------------
# orphan file cleanup
# ---------------------------------------------------------------------------


def _storage_patch(monkeypatch, tmp_path):
    import ximrato_server.services.storage as storage_mod

    monkeypatch.setattr(storage_mod, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_mod, "_AVATAR_DIR", tmp_path / "avatars")


def test_delete_removes_orphan_file(client, monkeypatch, tmp_path):
    """Deleting the only reference to a file removes it from disk."""
    _storage_patch(monkeypatch, tmp_path)
    tokens = _register(client, "orph1", "orph1@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("avatar.jpg", _jpeg((31, 31)), "image/jpeg")},
        headers=headers,
    )
    assert len(list((tmp_path / "avatars").iterdir())) == 1
    client.delete("/users/me/avatar", headers=headers)
    assert len(list((tmp_path / "avatars").iterdir())) == 0


def test_delete_keeps_shared_file(client, monkeypatch, tmp_path):
    """Deleting one reference keeps the file when another user still holds it."""
    _storage_patch(monkeypatch, tmp_path)
    img_bytes = _jpeg((32, 32))
    tokens_a = _register(client, "orph2a", "orph2a@example.com")
    tokens_b = _register(client, "orph2b", "orph2b@example.com")
    for tokens in (tokens_a, tokens_b):
        client.post(
            "/users/me/avatar",
            files={"file": ("avatar.jpg", img_bytes, "image/jpeg")},
            headers=_auth_header(tokens["access_token"]),
        )
    client.delete("/users/me/avatar", headers=_auth_header(tokens_a["access_token"]))
    assert len(list((tmp_path / "avatars").iterdir())) == 1


def test_upload_removes_old_orphan_file(client, monkeypatch, tmp_path):
    """Replacing an avatar removes the old file when no other user references it."""
    _storage_patch(monkeypatch, tmp_path)
    tokens = _register(client, "orph3", "orph3@example.com")
    headers = _auth_header(tokens["access_token"])
    client.post(
        "/users/me/avatar",
        files={"file": ("a.jpg", _jpeg((33, 33)), "image/jpeg")},
        headers=headers,
    )
    assert len(list((tmp_path / "avatars").iterdir())) == 1
    client.post(
        "/users/me/avatar",
        files={"file": ("b.jpg", _jpeg((34, 34)), "image/jpeg")},
        headers=headers,
    )
    assert len(list((tmp_path / "avatars").iterdir())) == 1


def test_upload_keeps_shared_old_file(client, monkeypatch, tmp_path):
    """Replacing an avatar keeps the old file when another user still references it."""
    _storage_patch(monkeypatch, tmp_path)
    img_bytes = _jpeg((35, 35))
    tokens_a = _register(client, "orph4a", "orph4a@example.com")
    tokens_b = _register(client, "orph4b", "orph4b@example.com")
    for tokens in (tokens_a, tokens_b):
        client.post(
            "/users/me/avatar",
            files={"file": ("a.jpg", img_bytes, "image/jpeg")},
            headers=_auth_header(tokens["access_token"]),
        )
    client.post(
        "/users/me/avatar",
        files={"file": ("b.jpg", _jpeg((36, 36)), "image/jpeg")},
        headers=_auth_header(tokens_a["access_token"]),
    )
    assert len(list((tmp_path / "avatars").iterdir())) == 2
