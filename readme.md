# Trekking Management Application

A full‑stack web application built with **Flask**, **SQLite**, **Redis**, **Celery**, **Vue 3**, and **Bootstrap 5** to manage trekking activities for an organization. The system supports three roles — **Admin**, **Trek Staff**, and **User (Trekker)** — each with a dedicated dashboard and workflow.

---

## Project Overview

The Trekking Management Application centralizes the entire trekking lifecycle — from trek creation and staff assignment to user bookings, reminders, and historical records. The system enforces **role‑based access control**, prevents overbooking, and uses background jobs for daily reminders, monthly reports, and CSV export of trekking history.

Key capabilities:

- Admin manages treks, users, and staff from a unified dashboard.
- Trek Staff manage only the treks assigned to them.
- Users browse, book, and track treks, and export their trekking history.

---

## Tech Stack

| Layer        | Technology                                  |
|-------------|----------------------------------------------|
| Backend     | Python, Flask, Flask‑SQLAlchemy, Flask‑Login |
| Database    | SQLite                                       |
| Caching     | Redis (via Flask‑Caching, `RedisCache`)      |
| Background  | Celery + Redis (worker + beat)               |
| Frontend    | Vue 3, Vue Router, Vite, Bootstrap 5         |
| Auth        | Flask‑Login (session‑based)                  |
| Email       | Mailpit (local SMTP testing server)          |
| HTTP Hooks  | Google Chat Webhook (optional)               |

Constraints satisfied:

- Flask for API  
- VueJS for UI (CLI/Vite only for tooling)  
- Jinja2 only for minimal entry/health templates  
- Bootstrap 5 as the only CSS framework  
- SQLite as the only database  
- Redis for caching and Celery jobs  

---

## User Roles

### Admin

- Auto‑seeded programmatically (no admin registration).
- Dashboard stats:
  - Total treks
  - Total users
  - Total staff
  - Total bookings
- Create, update, and delete treks.
- Add new trek staff and manage staff status (active/blacklisted).
- Assign staff to treks.
- View all users and bookings.
- Search and filter treks, users, and staff.
- Deactivate/blacklist users and staff.

### Trek Staff

- Login only (created by Admin; no self registration).
- Staff dashboard showing:
  - Treks assigned by Admin
  - Number of registered users per trek
- Manage only assigned treks via **My Treks**:
  - Update trek slots and status (open/ongoing/completed).
  - View and manage participant list.
  - Mark trek as started/completed.

### User (Trekker)

- Self‑register and log in.
- User dashboard showing:
  - Available treks
  - Booked treks
  - Trek status
- Can:
  - Browse and search treks.
  - Book treks (open status + slots available).
  - View booking status and full trekking history.
  - Edit their profile.
  - Trigger CSV export of their trekking history.

---

## Project Structure

```text
tma_submission_grade/
│
├── backend/
│   ├── app.py              
│   ├── config.py           
│   ├── extensions.py       
│   ├── tasks.py            
│   ├── requirements.txt    
│   │
│   ├── models/             
│   │   ├── user.py
│   │   ├── trek.py
│   │   ├── booking.py
│   │   ├── notification.py
│   │   └── export_job.py
│   │
│   ├── routes/            
│   │   ├── auth_routes.py
│   │   ├── admin_routes.py
│   │   ├── staff_routes.py
│   │   └── user_routes.py
│   │
│   ├── services/
│   │   ├── seed_service.py      
│   │   ├── reminder_service.py 
│   │   ├── report_service.py    
│   │   └── mail_service.py      
│   │
│   ├── export/             
│   ├── reports/            
│   └── instance/           
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   │
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/
│       ├── components/
│       ├── views/          
│       ├── services/       
│       └── styles/         
│
└── README.md
```

---

## Database Models

| Model         | Description                                                  |
|---------------|--------------------------------------------------------------|
| `User`        | Unified user model for all roles (admin, staff, user)       |
| `Trek`        | Trek details, status, capacity, and assigned staff          |
| `Booking`     | User booking for a trek, with status and payment info       |
| `Notification`| In‑app notifications for users                               |
| `ExportJob`   | CSV export job tracking (task ID, filename, status)         |

Relationships:

- User (admin/staff/user) identified by `role`.
- Trek has optional `assigned_staff_id` referencing `User`.
- Booking links `user_id` and `trek_id`.
- Notification and ExportJob both reference `user_id`.

---

## Background Jobs (Celery + Redis)

### Daily Reminders

- Task: `tasks.daily_reminder`
- Scheduled via Celery Beat (e.g., every day at 07:00).
- For upcoming/ongoing treks:
  - Adds `Notification` records.
  - Sends Google Chat messages (if webhook configured).
  - Sends reminder emails via Mailpit SMTP.

### Monthly Activity Report

- Task: `tasks.monthly_report`
- Runs on the first day of every month.
- Uses `build_monthly_html()` to calculate:
  - Total treks
  - Treks conducted/ongoing
  - Total participants
  - Popular treks
- Saves `reports/monthly_report.html`.
- Emails the report to `admin@tma.com` via Mailpit.

### CSV Export (User‑triggered)

- Task: `tasks.export_history_csv`
- Triggered from user dashboard.
- Exports user trekking history as CSV:
  - User ID
  - Trek Name
  - Location
  - Booking Status
  - Booking Date
  - Payment Status
- Saves file in `backend/export/` and marks ExportJob as `finished`.

---

## Caching (Redis)

Configured in `config.py`:

```python
CACHE_TYPE = 'RedisCache'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 120
```

Redis is used via Flask‑Caching to cache:

- Frequently accessed treks.
- Dashboard metrics.

This reduces load on SQLite and improves response times.

---

## Core Business Rules

- Prevent overbooking: `available_slots > 0` is required to book.
- Booking allowed only when trek status is `open`.
- Prevent duplicate bookings per (user, trek).
- Only Admin can create/manage treks and staff.
- Only assigned Staff can manage an assigned trek.
- Complete booking history retained for each user.

---

## Default Admin Credentials

Admin is created programmatically via `seed_admin()`:

| Field    | Value         |
|----------|---------------|
| Email    | admin@tma.com |
| Password | Admin@123     |

There is **no admin registration route**; this satisfies the requirement that admin must be created programmatically.

---

## How to Run the Project (All Terminals)

Below are **ready‑to‑use command blocks**, one per terminal. Paths assume this structure:

```text
C:\Users\<you>\...\tma_submission_grade\
```

Adjust the base path if your folder is different.

### Terminal 1 – Backend (Flask API)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend will start on `http://127.0.0.1:5000`.

---

### Terminal 2 – Frontend (Vue 3 + Vite)

```powershell
cd frontend
npm install
npm run dev
```

Frontend will  run on `http://localhost:5173`.

---

### Terminal 3 – Redis

If you have Redis installed as a service, just ensure it’s running.  
If you start it manually, use the appropriate command for your setup (for example on WSL or Windows port of Redis):

```powershell
redis-server
```

Redis must listen on `localhost:6379`.

---

### Terminal 4 – Celery Worker

```powershell
cd backend
.\venv\Scripts\activate
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```
---

### Terminal 5 – Celery Beat (Scheduler)

```powershell
cd backend
.\venv\Scripts\activate
celery -A tasks.celery_app beat --loglevel=info
```

This will schedule:

- `tasks.daily_reminder` at the configured time.
- `tasks.monthly_report` on the first day of each month.

---

### Terminal 6 – Mailpit (SMTP + Web UI)

```powershell

mailpit
```

Mailpit defaults:

- SMTP: `127.0.0.1:1025`
- Web UI: `http://localhost:8025`

Open the Mailpit web UI in your browser to see reminder and monthly report emails.

---

## Access URLs

- **Frontend (Vue):** `http://localhost:5173`
- **Backend health check:** `http://127.0.0.1:5000/api/health`
- **Mailpit UI:** `http://localhost:8025`

---

## Notes

- All three roles share a single `User` table with a `role` field, as required.
- Admin, staff, and users have unique DB IDs; the UI shows a separate **serial number column** (1, 2, 3, …) in Admin tables for better presentation.
- Mailpit is used only for local email testing; no real emails are sent.
- All Celery tasks (reminders, monthly report, CSV export) are created and run locally by the student.
