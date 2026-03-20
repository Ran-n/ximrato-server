[//]: # ( ---------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/03/19 13:06:17.162346 )
[//]: # (+ Revised: 	2026/03/20 09:55:10.659144 )
[//]: # ( ---------------------------------------------------------------------- )

# ximrato-server

FastAPI backend for [ximrato-app](../ximrato-app). Serves a REST API with JWT auth.

## Repos

| Repo | Role |
|------|------|
| [`ximrato-app`](https://github.com/Ran-n/ximrato-app) | Flet frontend |
| [`ximrato-server`](https://github.com/Ran-n/ximrato-server) | This repo — FastAPI backend |

## Running

```bash
uv run uvicorn main:app --reload
```

## v1 Progress

### Done
- Auth — register, login, token refresh (JWT, access + refresh tokens)
- `GET /users/me` — return current user's profile
- `PATCH /users/me` — update username, email, password
- Health endpoint — `GET /` and `GET /health`
- Structured logging — access log with timing, per-operation logs in all routers, 422 validation errors logged per field

### To Do
- Extended user profile — display name, sex, date of birth, height (static fields on `users` table)
- Unit config — `user_config` table, `GET/PATCH /users/me/config` (weight kg/lb, distance km/mi, height cm/in)
- Exercises — DB-seeded fixed list, `GET /exercises`
- Sessions — `POST /sessions` (create), `PATCH /sessions/{id}` (end), `GET /sessions` (history)
- Sets — `POST /sessions/{id}/sets`, `GET /sessions/{id}/sets`
- Cardio — `POST /cardio`, `GET /cardio` (history)
- Body metrics — `POST /body-metrics`, `GET /body-metrics` (history)

## Data Model

All tables have `created_at` and `updated_at`.

### Users & Profile
- `users` — credentials + static profile (display name, sex, date of birth, height)
- `user_config` — per-user unit preferences (kg/lb, km/mi, cm/in)

### Strength
- `exercises` — DB-seeded, fixed list for v1. Bodyweight exercises use `weight=0` + `bodyweight_counted` flag.
- `sessions` — `started_at`, `ended_at`
- `session_exercises` — join table with `order` column; same exercise can appear multiple times in one session
- `sets` — reps, weight (decimal), bodyweight_counted, RPE (integer 6–10), to_failure, logged_at (timestamptz), rest_seconds (integer, null for first set — denormalized for read performance)

### Cardio
- `cardio_exercises` — DB-seeded (running, cycling, rowing for v1)
- `cardio_logs` — single table for all cardio types with optional columns per type:
  - duration_seconds, distance, logged_at, rest_seconds
  - avg_heart_rate (optional)
  - elevation_gain (optional)
  - stroke_rate (optional, rowing)

### Body Metrics
- `body_metrics` — time-series log per user: weight, waist, chest, hips, neck, arms, thighs
- Height is static on the user profile, not in body_metrics

## v2 (deferred)
- HIIT / circuit training
- Sports logging
- Additional exercise categories (swimming, jump rope, etc.)
- Additional body measurements beyond the v1 set
