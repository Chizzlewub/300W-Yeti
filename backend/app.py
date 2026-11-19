import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

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
