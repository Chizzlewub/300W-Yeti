# Team Yeti Ticketing

The EC2 web tier uses Nginx to proxy requests to the Flask application on the middleware instance. Flask reads tickets from PostgreSQL on the database instance.

## Middleware

Install the Python dependencies from `backend/requirements.txt`. Set `PGHOST`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` in the service environment. The app uses PostgreSQL port 5432. From `backend/`, run `gunicorn --bind 0.0.0.0:8000 app:app`.

The dashboard is available at `/tickets` and the JSON endpoint at `/api/tickets`.

## Web

Use `deployment/nginx.conf.example` as a reference for the Nginx site. Replace `MIDDLEWARE_PRIVATE_IP` with the middleware instance's private IPv4 address.

## Database

The existing app expects a PostgreSQL table named `tickets` with columns `ticket_id`, `description`, `priority`, and `status`. Apply the schema in `database/schema.sql` to a fresh PostgreSQL database with `psql -v ON_ERROR_STOP=1 -d ticketing -f database/schema.sql`. Configure database roles and grants for the deployment environment separately.
