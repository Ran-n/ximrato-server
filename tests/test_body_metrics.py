#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/27 00:00:00.000000
Revised: 2026/03/27 20:18:21.196560
"""

_METRIC_TYPES = ("weight", "waist", "chest", "hips", "neck", "arms", "thighs")


def test_create_body_metric_weight(client, auth_headers):
    r = client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight", "value": 75.5})
    assert r.status_code == 201
    data = r.json()
    assert data["metric_type"] == "weight"
    assert data["value"] == 75.5
    assert "id" in data
    assert "logged_at" in data


def test_create_body_metric_all_types(client, auth_headers):
    for metric_type in _METRIC_TYPES:
        r = client.post(
            "/body-metrics",
            headers=auth_headers,
            json={"metric_type": metric_type, "value": 50.0},
        )
        assert r.status_code == 201, metric_type
        data = r.json()
        assert data["metric_type"] == metric_type
        assert data["value"] == 50.0


def test_create_body_metric_invalid_type(client, auth_headers):
    r = client.post("/body-metrics", headers=auth_headers, json={"metric_type": "bicep", "value": 35.0})
    assert r.status_code == 422


def test_create_body_metric_missing_value(client, auth_headers):
    r = client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight"})
    assert r.status_code == 422


def test_create_body_metric_missing_type(client, auth_headers):
    r = client.post("/body-metrics", headers=auth_headers, json={"value": 70.0})
    assert r.status_code == 422


def test_create_body_metric_requires_auth(client):
    r = client.post("/body-metrics", json={"metric_type": "weight", "value": 70.0})
    assert r.status_code == 401


def test_list_body_metrics_empty(client, auth_headers):
    r = client.get("/body-metrics", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_list_body_metrics_returns_own_entries(client, auth_headers):
    client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight", "value": 70.0})
    client.post("/body-metrics", headers=auth_headers, json={"metric_type": "waist", "value": 82.0})
    r = client.get("/body-metrics", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_body_metrics_excludes_other_users(client, auth_headers, other_headers):
    client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight", "value": 90.0})
    r = client.get("/body-metrics", headers=other_headers)
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_list_body_metrics_requires_auth(client):
    r = client.get("/body-metrics")
    assert r.status_code == 401


def test_list_body_metrics_ordered_newest_first(client, auth_headers):
    client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight", "value": 60.0})
    client.post("/body-metrics", headers=auth_headers, json={"metric_type": "weight", "value": 61.0})
    r = client.get("/body-metrics", headers=auth_headers)
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) == 2
    ids = [e["id"] for e in entries]
    assert ids == sorted(ids, reverse=True)


def test_create_body_metric_response_has_timestamps(client, auth_headers):
    r = client.post("/body-metrics", headers=auth_headers, json={"metric_type": "neck", "value": 37.5})
    assert r.status_code == 201
    data = r.json()
    assert "created_at" in data
    assert "updated_at" in data
    assert "logged_at" in data
