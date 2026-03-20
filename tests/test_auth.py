#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 07:39:41.912347
Revised: 2026/03/20 07:39:41.912347
"""


def test_register(client):
    r = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_username(client):
    payload = {"username": "dupeuser", "email": "a@example.com", "password": "pass"}
    client.post("/auth/register", json=payload)
    payload["email"] = "b@example.com"
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 409


def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"username": "u1", "email": "same@example.com", "password": "pass"},
    )
    r = client.post(
        "/auth/register",
        json={"username": "u2", "email": "same@example.com", "password": "pass"},
    )
    assert r.status_code == 409


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "pass",
        },
    )
    r = client.post("/auth/login", json={"username": "loginuser", "password": "pass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"username": "wpuser", "email": "wp@example.com", "password": "correct"},
    )
    r = client.post("/auth/login", json={"username": "wpuser", "password": "wrong"})
    assert r.status_code == 401


def test_refresh(client):
    r = client.post(
        "/auth/register",
        json={"username": "refuser", "email": "ref@example.com", "password": "pass"},
    )
    refresh_token = r.json()["refresh_token"]
    r2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_refresh_with_access_token_fails(client):
    r = client.post(
        "/auth/register",
        json={"username": "badref", "email": "badref@example.com", "password": "pass"},
    )
    access_token = r.json()["access_token"]
    r2 = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert r2.status_code == 401
