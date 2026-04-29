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
| Dashboard | `/home` | ✅ Done | 6 KPI cards loaded from `/stats`, 3×2 grid layout |
| Inventory | `/inventory` | ✅ Done | Full CRUD, role-gated, search + status + category filter |
| User Management | `/admin` | ✅ Done | SuperAdmin only — full CRUD for users |
| Loans | `/loans` | ❌ Stub | Model + API POST exist; UI not built |
| Handover | `/handover` | ❌ Stub | Model exists; UI not built |
| Reports | `/reports` | ❌ Stub | Not started |
| Notifications | `/notifications` | ❌ Stub | Not started |

---

## Full Feature Checklist (from spec)

### Module A — Inventory Management
- [x] Fields: name, category, inventory code, quantity, condition (new/good/worn), location, responsible person
- [x] List with search bar and filters (category, status)
- [ ] Filter by location
- [ ] Sortable table columns
- [ ] Photo upload per material (JPG/PNG)
- [ ] QR code auto-generation
- [ ] Export to Excel / PDF (all items and per item)
- [ ] Print QR code labels for physical tagging

### Module B — Loan Tracking (Check-Out / Check-In)
- [x] Loan DB model (material, quantity, borrower, reason, event date, deadline, condition, photos, accessories, deterioration flag, status)
- [x] Basic `POST /loans/` API endpoint
- [ ] Loan checkout UI (select material + quantity, borrower, reason, auto-deadline = event date + 2 days)
- [ ] Mandatory checkout photo (proof of condition)
- [ ] Loan return (check-in) UI with mandatory photo
- [ ] Side-by-side photo comparison (checkout vs check-in)
- [ ] Auto flag deterioration if condition changed; notify admin
- [ ] Active loans dashboard (days remaining with green/orange/red colors, quick "Return" button)
- [ ] Email: loan confirmation, 1-day-before reminder, overdue alert

### Module C — Handover (Between People / Departments)
- [x] Handover DB model (material, quantity, sender → receiver, condition before/after, photos, signatures, PDF path, status)
- [ ] Handover form UI (what, from whom, to whom, condition, photo)
- [ ] Receiver confirmation UI (verify quantity + condition, report differences)
- [ ] Digital signature capture
- [ ] Auto-generate "Proces Verbal" PDF with both signatures
- [ ] Full custody history (who had what and when)
- [ ] Status tracking: pending / completed
- [ ] Notification to admin/coordinator on handover events

### Reporting & Dashboard
- [ ] Monthly report: item count, top 5 most borrowed, return rate, deteriorations — export PDF
- [ ] Weekly report: active loans, this week's deadlines, overdue items, pending handovers — email + PDF
- [ ] Dashboard graphs: stock evolution, top 10 items, category distribution, rankings table

### Notification System
- [ ] Reminder 1 day before loan deadline
- [ ] Overdue alert when deadline is passed
- [ ] Monday morning digest of all active loans
- [ ] Low stock alert when quantity < 20
- [ ] Handover confirmation email to receiver

### Roles & Access Control
- [x] SuperAdmin — full access (inventory CRUD, user management, all pages)
- [x] Admin — inventory CRUD (create, edit, delete), manage loans
- [x] Coordinator — can edit inventory (not create/delete), can borrow
- [x] Vizualizator — read-only everywhere

---

## API Overview

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/login/` | None | Login — sets session cookie |
| POST | `/logout/` | Any | Clears session |
| GET | `/me` | Any | Returns current user info |
| GET | `/stats` | Any | Dashboard KPI numbers |

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

## Project Timeline (from spec)

| Phase | Weeks | Status |
|-------|-------|--------|
| 1. Analysis & design | 1–2 | ✅ DB schema, wireframes done |
| 2. Functional prototype | 3–5 | ✅ Inventory + auth + search done |
| 3. Advanced features | 6–8 | 🔄 Loans / handover / notifications — in progress |
| 4. Reporting & dashboard | 9–10 | ❌ Not started |
| 5. Testing & finalization | 11–12 | ❌ Not started |
| 6. Deployment | 13 | ❌ Not started |

---

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy (ORM) + SQLite + bcrypt
- **Sessions:** In-memory cookie-based sessions (`session_token` httponly cookie)
- **Frontend:** Vanilla HTML/CSS/JS — no framework, served as static files by FastAPI
- **i18n:** EN/RO via `langAndDarkMode.js` (localStorage key `lang`)
- **Theme:** Light/dark via CSS `data-theme` attribute (localStorage key `theme`)
