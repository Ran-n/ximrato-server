[//]: # ( ---------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/03/19 13:06:17.162346 )
[//]: # (+ Revised: 	2026/03/27 21:24:37.287616 )
[//]: # ( ---------------------------------------------------------------------- )

# ximrato-server

FastAPI backend for [ximrato-app](../ximrato-app/README.md). Serves a REST API with JWT auth.

## Repos

| Repo | Role |
|------|------|
| [`ximrato-app`](https://github.com/Ran-n/ximrato-app) | Flet frontend |
| [`ximrato-server`](https://github.com/Ran-n/ximrato-server) | This repo — FastAPI backend |

## Configuration

Copy `.env.example` to `.env` and set the values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `DATABASE_URL` | `sqlite:///./ximrato.db` | SQLAlchemy DB URL |
| `UPLOAD_DIR` | `static` | Directory for user-uploaded files |
| `BASE_URL` | `http://127.0.0.1:8000` | Public base URL (used to build avatar URLs); port is also used by uvicorn |

## Running

```bash
uv run uvicorn main:app --reload --host 0.0.0.0
```

## Testing

```bash
uv run pytest tests/ -v
```

## v1 Progress

### Done
- Auth — register, login, token refresh (JWT, access + refresh tokens)
- `GET /users/me` — return current user's profile
- `PATCH /users/me` — update username, email, password, display name, sex, date of birth, height
- `GET/PATCH /users/me/config` — unit preferences (weight kg/lb, distance km/mi, height cm/in); row created on first access
- Health endpoint — `GET /` and `GET /health`
- Structured logging — access log with timing, per-operation logs in all routers, 422 validation errors logged per field

- Exercises — DB-seeded fixed list (24 exercises across push/pull/legs/core), `GET /exercises`
- Sessions — `POST /sessions` (start), `GET /sessions/active`, `GET /sessions` (history), `PATCH /sessions/{id}/end`
- Sets — `POST /sessions/{id}/sets` (exercise, reps, weight, bodyweight_counted, RPE, to_failure)
- Avatar — `POST /users/me/avatar` (upload; resized to 128×128, WebP quality 85, transparency preserved), `DELETE /users/me/avatar`; file served via `/static/avatars/`; `avatar_url` returned in `GET /users/me`
- Cardio exercises — DB-seeded (Running, Cycling, Rowing), `GET /cardio/exercises`
- Cardio logs — `POST /cardio` (duration, distance, optional HR/elevation/stroke rate), `GET /cardio` (history, newest first)
- Auth events — `POST /auth/logout` (records logout event), `GET /auth/events` (history newest first); login and register also record events
- i18n — language preference stored in `user_config` (`language` field, FK → `languages`); supported: `en`, `gl`
- Body metrics — `POST /body-metrics` (one measurement per request; `metric_type` validated against `metric_types` lookup table), `GET /body-metrics` (history, newest first); deprecated HTTP status constants replaced

### To Do
- History views — past sessions, cardio logs, body metric trends

## Data Model

All tables have `created_at` and `updated_at`.

### Lookup Tables
- `event_types` — seeded: login, logout, register
- `exercise_categories` — seeded: push, pull, legs, core
- `rpe_levels` — seeded: no_reps_left, could_do_1, could_do_2, could_do_3, could_do_4_5, very_light
- `sexes` — seeded: male, female, other
- `weight_units` — seeded: kg, lb
- `distance_units` — seeded: km, mi
- `height_units` — seeded: cm, in
- `languages` — seeded: en, gl
- `metric_types` — seeded: weight, waist, chest, hips, neck, arms, thighs

### Users & Profile
- `users` — credentials + static profile (display name, `sex_id` → `sexes`, date of birth, height, `avatar_path`)
- `user_config` — per-user preferences (`weight_unit_id` → `weight_units`, `distance_unit_id` → `distance_units`, `height_unit_id` → `height_units`, `language_id` → `languages`)
- `auth_events` — per-user event log: `event_type_id` → `event_types`, `occurred_at`

### Strength
- `exercises` — DB-seeded, fixed list for v1. Bodyweight exercises use `weight=0` + `bodyweight_counted` flag. `category_id` → `exercise_categories`.
- `workout_sessions` — `started_at`, `ended_at` (null while active), `notes`
- `workout_sets` — `exercise_id`, `reps`, `weight`, `bodyweight_counted`, `rpe_level_id` → `rpe_levels`, `to_failure`, `logged_at`

### Cardio
- `cardio_exercises` — DB-seeded (running, cycling, rowing for v1)
- `cardio_logs` — single table for all cardio types with optional columns per type:
  - duration_seconds, distance, logged_at, rest_seconds
  - avg_heart_rate (optional)
  - elevation_gain (optional)
  - stroke_rate (optional, rowing)

### Body Metrics
- `body_metrics` — one row per measurement: `metric_type_id` → `metric_types`, `value`, `logged_at`; each metric type is logged independently
- Height is static on the user profile, not in body_metrics

## v2 (deferred)
- HIIT / circuit training
- Sports logging
- Additional exercise categories (swimming, jump rope, etc.)
- Additional body measurements beyond the v1 set
