# SupportDesk

A full-stack customer-support workspace built with **Django 6.1**, **Django REST Framework**, the **official Django MongoDB Backend**, and a **React/Vite** frontend.

## Features

- JWT authentication and Admin / Supervisor / Agent roles
- Customer directory with search, notes and tags
- Ticket lifecycle: Open, Pending, Resolved, Closed
- Priorities, categories, sources, assignees and ticket tags
- Threaded customer replies and private internal notes
- Reply suggestions using the OpenAI Responses API
- Knowledge base used as context for reply suggestions
- Dashboard ticket/customer metrics and workload distribution
- Team directory and admin-only role changes
- Activity/audit log
- Django Admin
- Demo seed command and production admin bootstrap
- Vercel frontend + Render backend deployment configuration

## Architecture

```text
React / Vite (Vercel)
        |
        | HTTPS + JWT
        v
Django REST API (Render)
        |
        +------> MongoDB Atlas
        |
        +------> OpenAI Responses API (optional; fallback reply works without key)
```

## Repository layout

```text
backend/              Django API
frontend/             React/Vite SPA
render.yaml           Render service blueprint
vercel.json           Vercel monorepo build config
```

## Backend environment variables

Copy `backend/.env.example` and configure these values in Render:

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Django signing secret |
| `MONGODB_URI` | Yes | MongoDB Atlas connection URI |
| `MONGODB_DB_NAME` | Yes | Database name, e.g. `supportdesk` |
| `CORS_ALLOWED_ORIGINS` | Yes | Frontend origins, comma-separated |
| `CSRF_TRUSTED_ORIGINS` | Yes | Trusted frontend origins |
| `ADMIN_USERNAME` | Yes | Initial production admin username |
| `ADMIN_PASSWORD` | Yes | Initial production admin password |
| `ADMIN_EMAIL` | Recommended | Initial admin email |
| `OPENAI_API_KEY` | Optional | Enables real AI suggestions |
| `OPENAI_MODEL` | Optional | Defaults to `gpt-5.6-luna` |
| `DEBUG` | No | Keep `False` in production |

Render automatically provides `PORT` and `RENDER_EXTERNAL_HOSTNAME`.

## Frontend environment variable

Configure in Vercel:

```env
VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com/api
```

## Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# configure environment values
python manage.py migrate
python manage.py bootstrap_admin
python manage.py runserver
```

Optional demo records:

```bash
python manage.py seed_demo
```

## Local frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Main API routes

- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /api/auth/me/`
- `GET /api/dashboard/stats/`
- `/api/customers/`
- `/api/tickets/`
- `POST /api/tickets/{id}/messages/`
- `POST /api/tickets/{id}/ai-suggest/`
- `POST /api/tickets/{id}/assign-to-me/`
- `POST /api/tickets/{id}/close/`
- `/api/knowledge/`
- `GET /api/activity/`
- `/api/team/`
- `GET /api/health/`

## Production notes

MongoDB's official Django backend uses MongoDB-compatible migrations for Django's `admin`, `auth`, and `contenttypes` apps. Those migration modules are committed under `backend/mongo_migrations/`. Business models use UUID primary keys while Django auth uses MongoDB ObjectIds.

Do not commit real secrets. Store all secrets in Render/Vercel environment settings.
