# UVT Branding App

Inventory management web app for Universitatea de Vest Timișoara. Tracks branding materials — loans, handovers, and stock.

---

## Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/install/windows)
- [Visual Studio Code](https://code.visualstudio.com/download) (recommended)

**Recommended VSCode extensions:** GitHub Pull Requests, Pylance, Python, Python Debugger, SQLite Viewer, SQLTools, SQLTools SQLite, HTML CSS Support, JavaScript and TypeScript Nightly

---

## Setup

**1. Clone the repo**
```
git clone https://github.com/Robert-Csatlos/UVTBrandingApp
```

**2. Configure git identity**
```
git config --global user.email "yourEmail@e-uvt.ro"
git config --global user.name "Your Name"
```

**3. Create and activate a virtual environment**
```
python -m venv venv
.\venv\Scripts\activate
```

**4. Install dependencies**
```
pip install -r requirements.txt
```

**5. Start the server**
```
python -m uvicorn backend.api:app --reload
```

The app runs at `http://127.0.0.1:8000`. Press `Ctrl+C` to stop.

> **Note:** Sessions are stored in memory and reset on server restart. The SQLite database (`database.db`) is created automatically on first run.

---

## User Roles

There are four roles, listed from most to least privileged:

| Role | Description |
|------|-------------|
| **SuperAdmin** | Full access to everything, including user management |
| **Admin** | Manages inventory and loans for their department |
| **Coordinator** | Can view and edit inventory; can create and manage loans |
| **Vizualizator** | Read-only access across the app |

---

## What Each Role Can Do

### Inventory Management (`/inventory`)

| Action | SuperAdmin | Admin | Coordinator | Vizualizator |
|--------|:---------:|:-----:|:-----------:|:------------:|
| View all items | ✅ | ✅ | ✅ | ✅ |
| Add new item | ✅ | ✅ | — | — |
| Edit item | ✅ | ✅ | ✅ | — |
| Delete item | ✅ | ✅ | — | — |

### User Management (`/admin`)

| Action | SuperAdmin | Admin | Coordinator | Vizualizator |
|--------|:---------:|:-----:|:-----------:|:------------:|
| View users | ✅ | — | — | — |
| Create user | ✅ | — | — | — |
| Edit user | ✅ | — | — | — |
| Delete user | ✅ | — | — | — |

### Dashboard (`/home`)

All roles can view the dashboard.

---

## Pages — Current Status

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Login | `/` | ✅ Done | Redirects to `/admin` (SuperAdmin) or `/home` (others) |
| Dashboard | `/home` | ✅ Done | KPI cards (values currently hardcoded) |
| Inventory | `/inventory` | ✅ Done | Full CRUD with role-based controls, search, filter |
| User Management | `/admin` | ✅ Done | SuperAdmin only — full CRUD for users |
| Loans | `/loans` | ❌ Stub | Not yet implemented |
| Handover | `/handover` | ❌ Stub | Not yet implemented |
| Reports | `/reports` | ❌ Stub | Not yet implemented |
| Notifications | `/notifications` | ❌ Stub | Not yet implemented |

---

## API Overview

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/login/` | None | Login — sets session cookie |
| POST | `/logout/` | Any | Clears session |
| GET | `/me` | Any | Returns current user info |

### Inventory
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/inventory/` | Any role | List all items |
| POST | `/inventory/` | Admin+ | Create item |
| GET | `/inventory/{id}` | Any role | Get single item |
| PUT | `/inventory/{id}` | Coordinator+ | Update item |
| DELETE | `/inventory/{id}` | Admin+ | Delete item |

### User Management
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/users/` | SuperAdmin | List all users |
| POST | `/admin/users/` | SuperAdmin | Create user |
| GET | `/admin/users/{id}` | SuperAdmin | Get user |
| PUT | `/admin/users/{id}` | SuperAdmin | Update user |
| DELETE | `/admin/users/{id}` | SuperAdmin | Delete user (cannot self-delete) |

---

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy (ORM) + SQLite + bcrypt
- **Sessions:** In-memory cookie-based sessions (`session_token` httponly cookie)
- **Frontend:** Vanilla HTML/CSS/JS — no framework, served as static files by FastAPI
- **i18n:** EN/RO via `langAndDarkMode.js` (localStorage key `lang`)
- **Theme:** Light/dark via CSS `data-theme` attribute (localStorage key `theme`)
