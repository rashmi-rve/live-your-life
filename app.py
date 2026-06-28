"""
Two-tier storybook app
======================
Tier 1 (this file): Flask serves every scene and exposes two small JSON
                     endpoints that the front-end calls when a visitor
                     writes their name on the nameplate or the award paper.
Tier 2 (MySQL):      house_entries / award_entries tables defined in
                     schema.sql store who reached which scene and when.

Run `schema.sql` once, copy .env.example to .env and fill in your MySQL
credentials, then `python app.py`.
"""
import os
import re
import uuid

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-secret-change-me")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "village_journey"),
}

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{0,119}$")


def get_db_connection():
    """Open a fresh connection for this request. Small app, no pool needed."""
    return mysql.connector.connect(**DB_CONFIG)


def get_session_id():
    if "sid" not in session:
        session["sid"] = uuid.uuid4().hex
    return session["sid"]


def clean_name(raw):
    name = (raw or "").strip()
    if not name or not NAME_RE.match(name):
        return None
    return name


@app.before_request
def ensure_session():
    get_session_id()


# ---------------------------------------------------------------- pages ----

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/home/box")
def home_box():
    return render_template("box.html")


@app.route("/home/village")
def home_village():
    houses = [
        {"size": 1, "label": "the little cottage"},
        {"size": 2, "label": "the cosy house"},
        {"size": 3, "label": "the wide house"},
        {"size": 4, "label": "the tall house"},
        {"size": 5, "label": "the grand house"},
    ]
    return render_template("village.html", houses=houses)


HOUSE_LABELS = {
    1: "the little cottage",
    2: "the cosy house",
    3: "the wide house",
    4: "the tall house",
    5: "the grand house",
}


@app.route("/home/house/<int:size>")
def home_house(size):
    if size < 1 or size > 5:
        size = 1
    return render_template("house.html", size=size, label=HOUSE_LABELS[size])


@app.route("/money")
def money_landing():
    return render_template("money_landing.html")


@app.route("/money/award")
def money_award():
    return render_template("award.html")


# -------------------------------------------------------------- api ----

@app.route("/api/save-house-entry", methods=["POST"])
def save_house_entry():
    data = request.get_json(silent=True) or {}
    name = clean_name(data.get("name"))
    house_size = data.get("house_size")

    if not name:
        return jsonify(ok=False, error="Please enter a name using letters only."), 400
    try:
        house_size = int(house_size)
        if not (1 <= house_size <= 5):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(ok=False, error="That house could not be found."), 400

    sid = get_session_id()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO house_entries (session_id, house_size, visitor_name) "
            "VALUES (%s, %s, %s)",
            (sid, house_size, name),
        )
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        app.logger.error("DB error saving house entry: %s", err)
        return jsonify(ok=False, error="Could not reach the village records right now."), 503

    return jsonify(ok=True, name=name)


@app.route("/api/save-award-entry", methods=["POST"])
def save_award_entry():
    data = request.get_json(silent=True) or {}
    name = clean_name(data.get("name"))

    if not name:
        return jsonify(ok=False, error="Please enter a name using letters only."), 400

    sid = get_session_id()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO award_entries (session_id, visitor_name) VALUES (%s, %s)",
            (sid, name),
        )
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        app.logger.error("DB error saving award entry: %s", err)
        return jsonify(ok=False, error="Could not reach the award records right now."), 503

    return jsonify(ok=True, name=name)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
