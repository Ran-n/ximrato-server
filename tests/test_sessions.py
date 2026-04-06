#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:25:00.000000
Revised: 2026/04/06 10:11:33.733175
"""


def test_get_active_returns_null_when_none(client, auth_headers):
    r = client.get("/sessions/active", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() is None


def test_start_session(client, auth_headers):
    r = client.post("/sessions", headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["started_at"] is not None
    assert data["ended_at"] is None
    assert data["sets"] == []


def test_start_session_409_when_already_active(client, auth_headers):
    client.post("/sessions", headers=auth_headers)
    r = client.post("/sessions", headers=auth_headers)
    assert r.status_code == 409


def test_get_active_returns_active_session(client, auth_headers):
    start_r = client.post("/sessions", headers=auth_headers)
    session_id = start_r.json()["id"]
    r = client.get("/sessions/active", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == session_id


def test_list_sessions_excludes_active(client, auth_headers):
    client.post("/sessions", headers=auth_headers)
    r = client.get("/sessions", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_end_session(client, auth_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.patch(f"/sessions/{session_id}/end", headers=auth_headers, json={})
    assert r.status_code == 200
    data = r.json()
    assert data["ended_at"] is not None
    assert data["notes"] is None


def test_end_session_with_notes(client, auth_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.patch(
        f"/sessions/{session_id}/end",
        headers=auth_headers,
        json={"notes": "great session"},
    )
    assert r.status_code == 200
    assert r.json()["notes"] == "great session"


def test_end_session_409_already_ended(client, auth_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    client.patch(f"/sessions/{session_id}/end", headers=auth_headers, json={})
    r = client.patch(f"/sessions/{session_id}/end", headers=auth_headers, json={})
    assert r.status_code == 409


def test_end_session_404_wrong_user(client, auth_headers, other_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.patch(f"/sessions/{session_id}/end", headers=other_headers, json={})
    assert r.status_code == 404


def test_list_sessions_includes_ended(client, auth_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    client.patch(f"/sessions/{session_id}/end", headers=auth_headers, json={})
    r = client.get("/sessions", headers=auth_headers)
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert session_id in ids


def test_add_set(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={"exercise_id": any_exercise_id, "reps": 10, "weight": 60.0},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["reps"] == 10
    assert data["weight"] == 60.0
    assert data["exercise"]["id"] == any_exercise_id
    assert data["bodyweight_counted"] is False
    assert data["to_failure"] is False
    assert data["rpe"] is None


def test_add_set_bodyweight(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={
            "exercise_id": any_exercise_id,
            "reps": 15,
            "weight": 0.0,
            "bodyweight_counted": True,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["weight"] == 0.0
    assert data["bodyweight_counted"] is True


def test_add_set_with_rpe_and_to_failure(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={
            "exercise_id": any_exercise_id,
            "reps": 5,
            "weight": 100.0,
            "rpe": "no_reps_left",
            "to_failure": True,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["rpe"] == "no_reps_left"
    assert data["to_failure"] is True


def test_add_set_nested_exercise_in_response(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={"exercise_id": any_exercise_id, "reps": 8, "weight": 40.0},
    )
    assert r.status_code == 201
    ex = r.json()["exercise"]
    assert "id" in ex
    assert "name" in ex
    assert "category" in ex


def test_add_set_appears_in_active_session(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={"exercise_id": any_exercise_id, "reps": 10, "weight": 50.0},
    )
    active = client.get("/sessions/active", headers=auth_headers).json()
    assert len(active["sets"]) == 1
    assert active["sets"][0]["reps"] == 10


def test_add_set_404_invalid_exercise(client, auth_headers):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={"exercise_id": 999999, "reps": 10, "weight": 60.0},
    )
    assert r.status_code == 404


def test_add_set_409_session_ended(client, auth_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    client.patch(f"/sessions/{session_id}/end", headers=auth_headers, json={})
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=auth_headers,
        json={"exercise_id": any_exercise_id, "reps": 10, "weight": 60.0},
    )
    assert r.status_code == 409


def test_add_set_404_wrong_user_session(client, auth_headers, other_headers, any_exercise_id):
    session_id = client.post("/sessions", headers=auth_headers).json()["id"]
    r = client.post(
        f"/sessions/{session_id}/sets",
        headers=other_headers,
        json={"exercise_id": any_exercise_id, "reps": 10, "weight": 60.0},
    )
    assert r.status_code == 404


def test_get_active_requires_auth(client):
    r = client.get("/sessions/active")
    assert r.status_code == 401


def test_list_sessions_requires_auth(client):
    r = client.get("/sessions")
    assert r.status_code == 401


def test_start_session_requires_auth(client):
    r = client.post("/sessions")
    assert r.status_code == 401


def test_end_session_requires_auth(client):
    r = client.patch("/sessions/1/end", json={})
    assert r.status_code == 401


def test_add_set_requires_auth(client):
    r = client.post("/sessions/1/sets", json={"exercise_id": 1, "reps": 1, "weight": 0.0})
    assert r.status_code == 401
