# Team Yeti Ticketing

The EC2 web tier uses Nginx to proxy requests to the Flask application on the middleware instance. Flask reads and writes tickets in PostgreSQL on the database instance.

## Middleware

Install the Python dependencies from `backend/requirements.txt`. Set `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, and `TICKETING_API_KEY` in the service environment. The app uses PostgreSQL port 5432. From `backend/`, run `gunicorn --bind 0.0.0.0:8000 app:app`.

Open `/` or `/tickets` to submit a ticket and view the list. The dashboard is accessible to anyone who can reach the website. The browser submits a regular HTML form to Flask. The JSON endpoint, `GET /api/tickets`, still requires the `X-API-Key` header.

## Web

Use `deployment/nginx.conf.example` as a reference for the Nginx site. Replace `MIDDLEWARE_PRIVATE_IP` with the middleware instance's private IPv4 address.

## Database

For a fresh database, apply the schema in `database/schema.sql` with `psql -v ON_ERROR_STOP=1 -d ticketing -f database/schema.sql`. The checked-in schema already supplies the ID sequence and defaults needed for ticket submission.

On the existing Ticketing-DB EC2 instance, connect with `sudo -u postgres psql -d ticketing` or use the table and sequence owner's account. Check the live sequence name and ticket ID default before applying grants.

```sql
SELECT pg_get_serial_sequence('public.tickets', 'ticket_id');
```

The checked-in schema returns `public.tickets_ticket_id_seq`. Use the actual sequence name and the role configured as `PGUSER` if either differs.

```sql
GRANT INSERT (description, priority, status) ON TABLE public.tickets TO ticketing_app;
GRANT USAGE ON SEQUENCE public.tickets_ticket_id_seq TO ticketing_app;
```

Keep the role's existing SELECT access to the four displayed columns. If the sequence lookup returns NULL, inspect `\d public.tickets` in psql. If the column default references a sequence, check its name and permissions directly. If the ID has no automatic default, the database owner must configure ID generation and initialize it above existing IDs before enabling submissions. The [PostgreSQL GRANT documentation](https://www.postgresql.org/docs/16/sql-grant.html) covers table and sequence privileges.
