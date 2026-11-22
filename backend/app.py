import os
import secrets

import psycopg
from flask import Flask, jsonify, redirect, render_template, request, url_for
from psycopg.rows import dict_row

app = Flask(__name__)
PRIORITIES = ("Low", "Medium", "High")
MAX_DESCRIPTION_LENGTH = 2000


def require_api_key():
    expected_key = os.environ.get("TICKETING_API_KEY")
    if not expected_key:
        return jsonify({"error": "API authentication is not configured"}), 503

    provided_key = request.headers.get("X-API-Key", "")
    if not secrets.compare_digest(provided_key.encode(), expected_key.encode()):
        return jsonify({"error": "Unauthorized"}), 401

    return None


def connect_db():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=5432,
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        row_factory=dict_row,
    )


def get_tickets():
    with connect_db() as conn:
        return conn.execute(
            "SELECT ticket_id, description, priority, status "
            "FROM tickets ORDER BY ticket_id"
        ).fetchall()


def insert_ticket(description, priority):
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO tickets (description, priority, status) VALUES (%s, %s, %s)",
            (description, priority, "Open"),
        )


@app.route("/api/tickets")
def api_tickets():
    auth_error = require_api_key()
    if auth_error is not None:
        return auth_error

    return jsonify(get_tickets())


@app.get("/")
def home():
    return redirect(url_for("display_tickets"))


@app.get("/tickets")
def display_tickets():
    return render_dashboard(submitted=request.args.get("submitted") == "1")


@app.post("/tickets")
def submit_ticket():
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "")

    if not description or len(description) > MAX_DESCRIPTION_LENGTH or "\0" in description:
        error = f"Enter a valid description of 1 to {MAX_DESCRIPTION_LENGTH} characters."
    elif priority not in PRIORITIES:
        error = "Choose Low, Medium, or High priority."
    else:
        try:
            insert_ticket(description, priority)
        except psycopg.Error:
            app.logger.exception("Could not save ticket")
            return render_dashboard(
                description=description, priority=priority,
                error="The ticket could not be saved. Please try again later.",
                status=503,
            )
        return redirect(url_for("display_tickets", submitted=1), code=303)

    return render_dashboard(
        description=description, priority=priority, error=error, status=400,
    )


def render_dashboard(description="", priority="Medium", error=None, status=200, submitted=False):
    try:
        tickets = get_tickets()
    except psycopg.Error:
        app.logger.exception("Could not load tickets")
        tickets = None
        status = 503

    return render_template(
        "tickets.html",
        tickets=tickets,
        priorities=PRIORITIES,
        max_description_length=MAX_DESCRIPTION_LENGTH,
        description=description,
        priority=priority,
        error=error,
        submitted=submitted,
    ), status
