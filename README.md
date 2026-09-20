# SupportDesk

SupportDesk is a customer-support workspace built with Django, Django REST Framework, MongoDB and React/Vite.

## What it includes

- JWT login with Admin, Supervisor and Agent roles
- Customer records and support history
- Ticket workflow with status, priority, source, category and assignee
- Customer replies and private internal notes
- AI-assisted reply suggestions
- Knowledge base
- Dashboard metrics
- Team management
- Activity log
- Django Admin
- Render backend and Vercel frontend configuration

## Stack

- Frontend: React + Vite
- Backend: Django 6.1 + Django REST Framework
- Database: MongoDB using the official Django MongoDB backend
- AI provider: CodeCraft API through its OpenAI-compatible chat-completions endpoint
- Backend hosting: Render
- Frontend hosting: Vercel

## Environment variables

### Render

```env
SECRET_KEY=...
DEBUG=False
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=supportdesk
ADMIN_USERNAME=admin
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
AI_API_KEY=...
AI_BASE_URL=https://codecraftapi.com/v1
AI_MODEL=gpt-5.6-sol
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app
```

Keep real credentials in Render/Vercel environment settings only. Do not commit them to GitHub.

### Vercel

The frontend currently falls back to the deployed Render API. You can also set:

```env
VITE_API_URL=https://supportdesk-api-8xjm.onrender.com/api
```

## Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_admin
python manage.py runserver
```

On Windows activate with:

```powershell
.venv\Scripts\activate
```

Optional demo data:

```bash
python manage.py seed_demo
```

## Local frontend

```bash
cd frontend
npm install
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
