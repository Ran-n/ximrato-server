#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:25:00.000000
Revised: 2026/03/20 13:35:28.552130
"""


def test_list_exercises_returns_all(client, auth_headers):
    r = client.get("/exercises", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 24


def test_list_exercises_has_expected_fields(client, auth_headers):
    r = client.get("/exercises", headers=auth_headers)
    ex = r.json()[0]
    assert "id" in ex
    assert "name" in ex
    assert "category" in ex


def test_list_exercises_sorted_by_category_then_name(client, auth_headers):
    r = client.get("/exercises", headers=auth_headers)
    data = r.json()
    pairs = [(ex["category"], ex["name"]) for ex in data]
    assert pairs == sorted(pairs)


def test_list_exercises_requires_auth(client):
    r = client.get("/exercises")
    assert r.status_code == 401
