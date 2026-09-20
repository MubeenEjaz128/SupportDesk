# SupportDesk

SupportDesk is a full-stack customer-support workspace built with Django, Django REST Framework, MongoDB and React/Vite.

It has separate experiences for customers and support staff. Customers can create an account, open support requests and follow only their own conversations. Agents work an assigned/unassigned queue, supervisors can oversee the full operation, and admins manage staff access.

## Current features

- Customer registration and login
- Admin / Supervisor / Agent / Customer roles
- Role-based backend access rules
- Customer-only ticket ownership
- Assigned + unassigned agent queue
- Internal notes hidden from customers
- Ticket status, priority, source, category and tags
- Customer and staff replies
- AI-assisted reply suggestions for support staff
- Knowledge base / customer help center
- Customer profile
- Team account creation, role changes and activation controls
- Activity log
- SMTP-ready customer reply emails
- Django Admin
- Render backend and Vercel frontend configuration

## Stack

- Frontend: React + Vite
- Backend: Django + Django REST Framework
- Database: MongoDB using the official Django MongoDB backend
- Authentication: JWT
- AI: CodeCraft API through an OpenAI-compatible chat-completions endpoint
- Backend hosting: Render
- Frontend hosting: Vercel

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

Windows:

```powershell
.venv\Scripts\activate
```

## Local frontend

```bash
cd frontend
npm install
npm run dev
```

## Main environment variables

See `backend/.env.example` for the complete list.

```env
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=supportdesk
ADMIN_USERNAME=admin
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
AI_API_KEY=...
AI_BASE_URL=https://codecraftapi.com/v1
AI_MODEL=gpt-5.6-sol
```

Keep real credentials in Render/Vercel environment settings. Never commit them.

## Project direction

The staged roadmap is documented in `docs/IMPLEMENTATION_PLAN.md`.
