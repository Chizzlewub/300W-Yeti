import os
import secrets
import psycopg

from psycopg.rows import dict_row
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
def require_api_key():
    expected_key = os.environ.get("TICKETING_API_KEY")

    if not expected_key:
        return jsonify({"error": "API authentication is not configured"}), 503

    provided_key = request.headers.get("X-API-Key", "")

    if not secrets.compare_digest(provided_key, expected_key):
        return jsonify({"error": "Unauthorized"}), 401

    return None

def get_tickets():
    with psycopg.connect(
        host=os.environ["PGHOST"],
        port=5432,
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        row_factory=dict_row
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ticket_id, description, priority, status "
                "FROM tickets ORDER BY ticket_id"
            )
            return cursor.fetchall()

@app.route("/api/tickets")
def api_tickets():
    auth_error = require_api_key()

    if auth_error is not None:
        return auth_error

    return jsonify(get_tickets())

@app.route("/tickets")
def display_tickets():
    tickets = get_tickets()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support Tickets</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 12px; }
            th { background-color: #eee; }
        </style>
    </head>
    <body>
        <h1>Support Ticket Dashboard</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Description</th>
                <th>Priority</th>
                <th>Status</th>
            </tr>
            {% for ticket in tickets %}
            <tr>
                <td>{{ ticket.ticket_id }}</td>
                <td>{{ ticket.description }}</td>
                <td>{{ ticket.priority }}</td>
                <td>{{ ticket.status }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, tickets=tickets)
