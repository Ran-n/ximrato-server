#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/06 00:00:00.000000
Revised: 2026/04/06 08:54:01.477162
"""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.banned_ip import BannedIP
from ximrato_server.security import BANNED_IPS


@pytest.fixture(autouse=True)
def clear_banned_ips():
    BANNED_IPS.clear()
    yield
    BANNED_IPS.clear()


# --- honeypot responses ---


def test_admin_returns_html(client):
    r = client.get("/admin", headers={"X-Forwarded-For": "1.2.3.4"})
    assert r.status_code == 200
    assert "Admin Panel" in r.text


def test_admin_login_get_returns_html(client):
    r = client.get("/admin/login", headers={"X-Forwarded-For": "1.2.3.5"})
    assert r.status_code == 200
    assert "Admin Panel" in r.text


def test_wp_admin_returns_html(client):
    r = client.get("/wp-admin", headers={"X-Forwarded-For": "1.2.3.6"})
    assert r.status_code == 200
    assert "Admin Panel" in r.text


def test_phpmyadmin_returns_html(client):
    r = client.get("/phpmyadmin", headers={"X-Forwarded-For": "1.2.3.7"})
    assert r.status_code == 200
    assert "Admin Panel" in r.text


def test_env_returns_plaintext(client):
    r = client.get("/.env", headers={"X-Forwarded-For": "1.2.3.8"})
    assert r.status_code == 200
    assert "DATABASE_URL" in r.text


def test_config_php_returns_plaintext(client):
    r = client.get("/config.php", headers={"X-Forwarded-For": "1.2.3.9"})
    assert r.status_code == 200
    assert "DATABASE_URL" in r.text


def test_git_config_returns_plaintext(client):
    r = client.get("/.git/config", headers={"X-Forwarded-For": "1.2.3.10"})
    assert r.status_code == 200
    assert "DATABASE_URL" in r.text


def test_admin_login_post_shows_invalid(client):
    r = client.post(
        "/admin/login",
        headers={"X-Forwarded-For": "1.2.3.11"},
        data={"username": "admin", "password": "admin"},
    )
    assert r.status_code == 200
    assert "Invalid" in r.text


# --- ip banning ---


def test_honeypot_hit_adds_ip_to_memory(client):
    client.get("/admin", headers={"X-Forwarded-For": "2.0.0.1"})
    assert "2.0.0.1" in BANNED_IPS


def test_honeypot_hit_persists_to_db(client, engine):
    client.get("/admin", headers={"X-Forwarded-For": "2.0.0.2"})
    with Session(engine) as db:
        row = db.scalar(select(BannedIP).where(BannedIP.ip == "2.0.0.2"))
    assert row is not None
    assert "honeypot" in row.reason


def test_duplicate_hit_does_not_create_second_db_row(client, engine):
    headers = {"X-Forwarded-For": "2.0.0.3"}
    client.get("/admin", headers=headers)
    client.get("/admin", headers=headers)
    with Session(engine) as db:
        rows = db.scalars(select(BannedIP).where(BannedIP.ip == "2.0.0.3")).all()
    assert len(rows) == 1


# --- middleware blocking ---


def test_banned_ip_is_blocked_on_subsequent_request(client):
    ip = "3.0.0.1"
    headers = {"X-Forwarded-For": ip}
    client.get("/admin", headers=headers)
    r = client.get("/health", headers=headers)
    assert r.status_code == 404


def test_banned_ip_blocked_on_auth_endpoint(client):
    ip = "3.0.0.2"
    headers = {"X-Forwarded-For": ip}
    client.get("/admin", headers=headers)
    r = client.post("/auth/login", json={"username": "x", "password": "y"}, headers=headers)
    assert r.status_code == 404


def test_clean_ip_is_not_blocked(client):
    r = client.get("/health", headers={"X-Forwarded-For": "4.0.0.1"})
    assert r.status_code == 200


# --- ip extraction ---


def test_x_real_ip_header_is_used(client):
    client.get("/admin", headers={"X-Real-IP": "5.0.0.1"})
    assert "5.0.0.1" in BANNED_IPS


def test_forwarded_for_takes_priority_over_real_ip(client):
    client.get(
        "/admin",
        headers={"X-Forwarded-For": "5.0.0.2, 10.0.0.1", "X-Real-IP": "5.0.0.3"},
    )
    assert "5.0.0.2" in BANNED_IPS
    assert "5.0.0.3" not in BANNED_IPS


def test_forwarded_for_first_address_is_used(client):
    client.get("/admin", headers={"X-Forwarded-For": "5.0.0.4, 10.0.0.2, 172.16.0.1"})
    assert "5.0.0.4" in BANNED_IPS
