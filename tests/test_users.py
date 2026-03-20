#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 10:41:15.000000
Revised: 2026/03/20 13:35:28.478079
"""

import pytest

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _register(client, username="u", email="u@example.com", password="pass"):
    r = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code == 201
    return r.json()


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------


def test_get_me(client):
    tokens = _register(client, "getme", "getme@example.com")
    r = client.get("/users/me", headers=_auth_header(tokens["access_token"]))
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "getme"
    assert data["email"] == "getme@example.com"
    assert data["display_name"] is None
    assert data["sex"] is None
    assert data["date_of_birth"] is None
    assert data["height"] is None


def test_get_me_unauthenticated(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_get_me_invalid_token(client):
    r = client.get("/users/me", headers=_auth_header("badtoken"))
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# PATCH /users/me — credentials
# ---------------------------------------------------------------------------


def test_update_username(client):
    tokens = _register(client, "oldname", "oldname@example.com")
    headers = _auth_header(tokens["access_token"])
    r = client.patch("/users/me", json={"username": "newname"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "newname"


def test_update_email(client):
    tokens = _register(client, "emailuser", "old@example.com")
    headers = _auth_header(tokens["access_token"])
    r = client.patch("/users/me", json={"email": "new@example.com"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "new@example.com"


def test_update_username_conflict(client):
    _register(client, "taken", "taken@example.com")
    tokens = _register(client, "other", "other@example.com")
    r = client.patch(
        "/users/me",
        json={"username": "taken"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 409


def test_update_email_conflict(client):
    _register(client, "emailA", "conflict@example.com")
    tokens = _register(client, "emailB", "emailB@example.com")
    r = client.patch(
        "/users/me",
        json={"email": "conflict@example.com"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 409


def test_update_password_correct_current(client):
    tokens = _register(client, "pwuser", "pw@example.com", password="old")
    headers = _auth_header(tokens["access_token"])
    r = client.patch(
        "/users/me",
        json={"current_password": "old", "password": "new"},
        headers=headers,
    )
    assert r.status_code == 200
    # verify new password works
    login = client.post("/auth/login", json={"username": "pwuser", "password": "new"})
    assert login.status_code == 200


def test_update_password_wrong_current(client):
    tokens = _register(client, "badpw", "badpw@example.com", password="correct")
    r = client.patch(
        "/users/me",
        json={"current_password": "wrong", "password": "new"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 400


def test_update_password_missing_current(client):
    tokens = _register(client, "nopw", "nopw@example.com", password="pass")
    r = client.patch(
        "/users/me",
        json={"password": "new"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /users/me — profile fields
# ---------------------------------------------------------------------------


def test_update_profile_fields(client):
    tokens = _register(client, "profile1", "profile1@example.com")
    headers = _auth_header(tokens["access_token"])
    r = client.patch(
        "/users/me",
        json={
            "display_name": "Alice",
            "sex": "female",
            "date_of_birth": "1990-06-15",
            "height": 165.5,
        },
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["display_name"] == "Alice"
    assert data["sex"] == "female"
    assert data["date_of_birth"] == "1990-06-15"
    assert data["height"] == pytest.approx(165.5)


def test_update_sex_invalid(client):
    tokens = _register(client, "badsex", "badsex@example.com")
    r = client.patch(
        "/users/me",
        json={"sex": "unknown"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /users/me/config
# ---------------------------------------------------------------------------


def test_get_config_defaults(client):
    tokens = _register(client, "cfg1", "cfg1@example.com")
    r = client.get("/users/me/config", headers=_auth_header(tokens["access_token"]))
    assert r.status_code == 200
    data = r.json()
    assert data["weight_unit"] == "kg"
    assert data["distance_unit"] == "km"
    assert data["height_unit"] == "cm"


def test_get_config_idempotent(client):
    tokens = _register(client, "cfg2", "cfg2@example.com")
    headers = _auth_header(tokens["access_token"])
    r1 = client.get("/users/me/config", headers=headers)
    r2 = client.get("/users/me/config", headers=headers)
    assert r1.json() == r2.json()


# ---------------------------------------------------------------------------
# PATCH /users/me/config
# ---------------------------------------------------------------------------


def test_update_config(client):
    tokens = _register(client, "cfg3", "cfg3@example.com")
    headers = _auth_header(tokens["access_token"])
    r = client.patch(
        "/users/me/config",
        json={"weight_unit": "lb", "distance_unit": "mi", "height_unit": "in"},
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["weight_unit"] == "lb"
    assert data["distance_unit"] == "mi"
    assert data["height_unit"] == "in"


def test_update_config_partial(client):
    tokens = _register(client, "cfg4", "cfg4@example.com")
    headers = _auth_header(tokens["access_token"])
    client.patch("/users/me/config", json={"weight_unit": "lb"}, headers=headers)
    r = client.get("/users/me/config", headers=headers)
    data = r.json()
    assert data["weight_unit"] == "lb"
    assert data["distance_unit"] == "km"  # unchanged


def test_update_config_invalid_unit(client):
    tokens = _register(client, "cfg5", "cfg5@example.com")
    r = client.patch(
        "/users/me/config",
        json={"weight_unit": "stone"},
        headers=_auth_header(tokens["access_token"]),
    )
    assert r.status_code == 422
