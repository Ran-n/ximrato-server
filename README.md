[//]: # ( ---------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/03/19 13:06:17.162346 )
[//]: # (+ Revised: 	2026/03/19 14:31:51.141360 )
[//]: # ( ---------------------------------------------------------------------- )

# ximrato-server

FastAPI backend for [ximrato-app](../ximrato-app). Serves a REST API with JWT auth.

## Repos

| Repo | Role |
|------|------|
| [`ximrato-app`](https://github.com/Ran-n/ximrato-app) | Flet frontend |
| [`ximrato-server`](https://github.com/Ran-n/ximrato-server) | This repo — FastAPI backend |

## v1 Scope

### Auth
- Self-registration endpoint
- JWT login / token refresh

### Data Model

All tables have `created_at` and `updated_at`.

#### Users & Profile
- `users` — credentials + static profile (display name, sex, date of birth, height)
- `user_config` — per-user unit preferences (kg/lb, km/mi, cm/in)

#### Strength
- `exercises` — DB-seeded, fixed list for v1. Bodyweight exercises use `weight=0` + `bodyweight_counted` flag.
- `sessions` — `started_at`, `ended_at`
- `session_exercises` — join table with `order` column; same exercise can appear multiple times in one session
- `sets` — reps, weight (decimal), bodyweight_counted, RPE (integer 6–10), to_failure, logged_at (timestamptz), rest_seconds (integer, null for first set — denormalized for read performance)

#### Cardio
- `cardio_exercises` — DB-seeded (running, cycling, rowing for v1)
- `cardio_logs` — single table for all cardio types with optional columns per type:
  - duration_seconds, distance, logged_at, rest_seconds
  - avg_heart_rate (optional)
  - elevation_gain (optional)
  - stroke_rate (optional, rowing)

#### Body Metrics
- `body_metrics` — time-series log per user: weight, waist, chest, hips, neck, arms, thighs
- Height is static on the user profile, not in body_metrics

### API Surface (v1)
- Auth: register, login, refresh
- Profile: get/update static profile, get/update unit config
- Exercises: list (seeded, read-only in v1)
- Sessions: create, end, get history
- Sets: log set within session, list sets for session/exercise
- Cardio: quick-log entry, list history
- Body metrics: log entry, list history

## v2 (deferred)
- HIIT / circuit training
- Sports logging
- Additional exercise categories (swimming, jump rope, etc.)
- Additional body measurements beyond the v1 set
