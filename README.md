# Live your life — Two-Tier Flask + MySQL App

A small interactive storybook web app. **Tier 1** is Flask, serving every
scene and two JSON endpoints. **Tier 2** is MySQL, which remembers the
names visitors write on the nameplate and the award certificate.

## The journey

```
Landing
 ├─ "Build a home"
 │    └─ Wooden box (tap → find the key)
 │         └─ Village (5 houses, tap one)
 │              └─ Nameplate → door opens → lunch plate → bedroom
 │                   "Sleep well and enjoy peace! 🌻"
 │
 └─ "Collect the amount" (₹100 crore)
      └─ Two circles
           ├─ "Return the money"            → back to Landing
           └─ "Bring development…"
                └─ Certificate paper (write your name)
                     └─ Magical cup — "You deserve this award."
```

Every illustration (the box, the houses, the door, the food plate, the
bedroom, the certificate, the cup) is hand-drawn inline SVG — no external
image files — styled as a "papercut diorama" with a sky that shifts mood
(day → dusk → night, or dawn for the award) as the story moves forward.

## Run it with Docker (recommended)

This spins up both tiers — the Flask app and a MySQL container — and
loads `schema.sql` into MySQL automatically the first time it starts.

```bash
cp .env.example .env       # edit FLASK_SECRET_KEY and DB_PASSWORD
docker compose up --build
```

Visit **http://localhost:5000**.

- `docker compose down` stops both containers (data is kept, in the
  `db_data` volume).
- `docker compose down -v` stops them **and deletes** the database data —
  use this if you change `schema.sql` and want it to run again from
  scratch.
- `docker compose logs -f web` tails the Flask app's logs.

The app container (`Dockerfile`) runs as a non-root user behind
`gunicorn`, and has a healthcheck that pings `/`. The database container
won't be marked ready — and the app won't start — until MySQL actually
accepts connections.

## Run it manually (no Docker)

#### 1. Set up MySQL

```bash
mysql -u root -p < schema.sql
```

This creates a `village_journey` database with two tables:

- `house_entries` — session_id, house_size (1–5), visitor_name, created_at
- `award_entries` — session_id, visitor_name, created_at

#### 2. Configure the app

```bash
cp .env.example .env
```

Edit `.env` with your MySQL host/user/password and a random
`FLASK_SECRET_KEY` (used to sign the session cookie that tracks each
visitor's journey).

#### 3. Install dependencies & run

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Visit **http://localhost:5000**.

## Project layout

```
app.py                  Flask routes + the two /api/save-* endpoints
schema.sql               MySQL table definitions
requirements.txt
.env.example
Dockerfile                Image for the Flask app (gunicorn, non-root, healthcheck)
docker-compose.yml         Runs the app + MySQL together, loads schema.sql on first boot
.dockerignore
static/css/style.css     All visual design (one shared stylesheet)
static/js/main.js        Shared fetch() helper used by the two forms
templates/
  base.html               <head>, fonts, shared scaffolding
  landing.html             Opening choice
  box.html                 Wooden box → key
  village.html              5 houses
  house.html                Nameplate → door → food → bed (one page, 3 steps)
  money_landing.html        Two circles
  award.html                Certificate → magical cup (one page, 2 steps)
  partials/hills.html       Reusable layered hill silhouette
  partials/stars.html       Reusable night-sky star field
```

## Notes

- Names are validated server-side (letters, spaces, `.`, `'`, `-` only,
  1–120 characters) before being written to MySQL.
- Each visitor gets a random session id (stored in a signed cookie) so
  their `house_entries`/`award_entries` rows can be traced back to one
  visit if you ever want to look at the data — no personal data beyond
  the name they typed is collected.
- If MySQL is unreachable, the two save endpoints return a friendly
  error (HTTP 503) instead of crashing the app; every other screen keeps
  working since it doesn't touch the database.
- Inside Docker the app runs under `gunicorn` instead of Flask's dev
  server. Running `python app.py` directly (outside Docker) still uses
  Flask's built-in server, which is fine for local development.

# Author

Rashmi
