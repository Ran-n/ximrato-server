#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:25:00.000000
Revised: 2026/03/24 07:36:02.472204
"""

import itertools
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from main import app
from ximrato_server.database import Base, get_db
from ximrato_server.seed import seed_exercises

_counter = itertools.count(1)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    with Session(eng) as db:
        seed_exercises(db)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture
def client(engine):
    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with patch("main.engine", engine):
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    n = next(_counter)
    r = client.post(
        "/auth/register",
        json={
            "username": f"testuser{n}",
            "email": f"testuser{n}@example.com",
            "password": "testpass1",
        },
    )
    assert r.status_code == 201
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_headers(client):
    n = next(_counter)
    r = client.post(
        "/auth/register",
        json={
            "username": f"other{n}",
            "email": f"other{n}@example.com",
            "password": "testpass1",
        },
    )
    assert r.status_code == 201
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def any_exercise_id(client):
    n = next(_counter)
    r = client.post(
        "/auth/register",
        json={
            "username": f"exuser{n}",
            "email": f"exuser{n}@example.com",
            "password": "testpass1",
        },
    )
    token = r.json()["access_token"]
    r = client.get("/exercises", headers={"Authorization": f"Bearer {token}"})
    return r.json()[0]["id"]
