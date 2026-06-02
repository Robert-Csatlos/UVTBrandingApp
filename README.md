# UVT Branding App

Inventory and loan management web app for Universitatea de Vest Timisoara branding materials. The app tracks stock, loans, returns, handovers, notifications, reports, and material condition.

---

## Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/install/windows)
- [Visual Studio Code](https://code.visualstudio.com/download) (recommended)

Recommended VS Code extensions: GitHub Pull Requests, Pylance, Python, Python Debugger, SQLite Viewer, SQLTools, SQLTools SQLite, HTML CSS Support, JavaScript and TypeScript Nightly.

---

## Setup

**1. Clone the repo**

```powershell
git clone https://github.com/Robert-Csatlos/UVTBrandingApp
```

**2. Configure git identity**

```powershell
git config --global user.email "yourEmail@e-uvt.ro"
git config --global user.name "Your Name"
```

**3. Create and activate a virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**4. Install dependencies**

```powershell
pip install -r requirements.txt
```

**5. Start the server**

```powershell
python -m uvicorn backend.api:app --reload
```

The app runs at `http://127.0.0.1:8000`. Press `Ctrl+C` to stop.

Sessions are stored in memory and reset on server restart. The SQLite database (`database.db`) is created automatically on first run.

---

## Demo Users

Seed users are defined in `seed_users.py`.

| Role | Email | Password |
|------|-------|----------|
| SuperAdmin | `superadmin@e-uvt.ro` | `superadmin` |
| Admin | `admin.dept@e-uvt.ro` | `admin1234` |
| Coordinator | `coordinator@e-uvt.ro` | `coord1234` |
| Vizualizator | `vizualizator@e-uvt.ro` | `viz123456` |

---

## User Roles

| Role | Description |
|------|-------------|
| SuperAdmin | Full access to everything, including user management |
| Admin | Manages inventory, loans, reports, and operational notifications |
| Coordinator | Can view/edit inventory and manage loans/handovers |
| Vizualizator | Read-only access where allowed |

---

## Pages

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Login | `/` | Done | Professional landing/login flow with light/dark theme switch |
| Dashboard | `/home` | Done | KPI cards from `/stats` with semantic colors: red for overdue/low stock, yellow for attention, green for healthy stock, blue for totals |
| Inventory | `/inventory` | Done | CRUD, search, category/status filters, loan checkout, and condition variants |
| Loans | `/loans` | Done | Active/returned/overdue list, return flow with photo, deterioration flag, and manual reminder |
| Handover | `/handover` | Done | Create handovers, receiver confirmation, condition before/after, photos, and signature capture |
| Reports | `/reports` | Done | KPI summary, timeline, category/top item/user activity views, overdue list, inventory status, CSV export |
| Notifications | `/notifications` | Done | Notification inbox, unread badge, filters, mark-read, clear, and sidebar badge |
| User Management | `/admin` | Done | SuperAdmin-only CRUD for users |

---

## Current UX Notes

- The Romanian language switch was removed from all pages.
- The app keeps only the light/dark mode switch.
- The notification badge appears only on the Notifications sidebar item, not on Loans.
- The notification badge is global and can appear from any page that has the sidebar notification box.
- Dashboard and Reports use logical KPI colors:
  - Red: overdue, deteriorated, low stock, or other urgent/problem states.
  - Yellow: active loans and due-soon attention states.
  - Green: available/returned/healthy states.
  - Blue: neutral totals and general activity.

---

## Inventory Condition Variants

Inventory items are separated by condition so a returned damaged item does not turn the full stock into damaged stock.

Condition codes:

| Condition | Code suffix | Example |
|-----------|-------------|---------|
| New | `-N` | `BAN-001-N` |
| Good | `-G` | `BAN-001-G` |
| Worn / Damaged | `-W` | `BAN-001-W` |

The inventory UI includes a Variants popup that groups items by base code and shows stock per condition. Checkout uses the selected item's condition. Return flows can place stock back into the correct condition variant.

---

## Feature Checklist

### Inventory Management

- [x] Fields: name, category, inventory code, quantity, condition, location, responsible person
- [x] Search and filters by category/status
- [x] Role-gated create/edit/delete behavior
- [x] Condition-specific variants using `-N`, `-G`, and `-W` suffixes
- [x] Variants popup per item/base code
- [ ] Filter by location
- [ ] Sortable table columns
- [ ] Photo upload per material
- [ ] QR code auto-generation
- [ ] Export to Excel/PDF
- [ ] Print QR code labels

### Loan Tracking

- [x] Loan database model and API
- [x] Checkout UI from Inventory
- [x] Mandatory checkout photo
- [x] Auto deadline support from event date
- [x] Loan dashboard with search/status filters
- [x] Return/check-in UI with mandatory photo
- [x] Condition on return
- [x] Deterioration flag
- [x] Manual reminder notification
- [ ] Side-by-side photo comparison layout
- [ ] Email delivery for confirmation/reminders/overdue alerts

### Handover

- [x] Handover database model and API
- [x] Handover form UI
- [x] Receiver confirmation UI
- [x] Condition before/after tracking
- [x] Photo support
- [x] Digital signature capture
- [x] Status tracking: pending/completed
- [ ] Auto-generated "Proces Verbal" PDF
- [ ] Full custody history view
- [ ] Email notifications for handover events

### Reporting & Dashboard

- [x] Dashboard KPI cards
- [x] Semantic color states for KPI cards
- [x] Reports summary cards
- [x] Loan timeline
- [x] Category distribution
- [x] Top borrowed items
- [x] User activity
- [x] Overdue list
- [x] Inventory status summary
- [x] CSV export
- [ ] Scheduled monthly/weekly PDF reports
- [ ] Email digest delivery

### Notifications

- [x] In-app notification model and API
- [x] Sidebar unread notification badge
- [x] Notification inbox page
- [x] Due-soon notifications
- [x] Overdue notifications
- [x] Low stock notifications
- [x] Return and deterioration notifications
- [x] Mark one/all as read
- [x] Clear notifications
- [ ] Email/SMS notification delivery
- [ ] Monday morning digest

### Roles & Access Control

- [x] SuperAdmin: full access
- [x] Admin: inventory CRUD, loans, reports, notifications
- [x] Coordinator: inventory edit, loans, handovers, notifications
- [x] Vizualizator: read-only access where allowed

---

## API Overview

### Auth and Dashboard

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/login/` | Public | Login and set session cookie |
| POST | `/logout/` | Any role | Clear session |
| GET | `/me` | Any role | Current user |
| GET | `/stats` | Any role | Dashboard KPI numbers |

### Inventory

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/inventory/` | Any role | List inventory items |
| POST | `/inventory/` | Admin+ | Create item |
| GET | `/inventory/{id}` | Any role | Get one item |
| PUT | `/inventory/{id}` | Coordinator+ | Update item |
| DELETE | `/inventory/{id}` | Admin+ | Delete item |

### Loans

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/loans/` | Any role | List loans |
| POST | `/loans/` | Coordinator+ | Create loan |
| POST | `/loans/{id}/return` | Admin+ | Return/check in loan |
| POST | `/loans/{id}/deteriorated` | Admin+ | Flag loan as deteriorated |
| POST | `/loans/{id}/notify` | Admin+ | Send manual reminder notification |

### Handovers

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/handovers/` | Any role | List handovers |
| POST | `/handovers/` | Any role | Create handover |
| POST | `/handovers/{id}/confirm` | Any role | Confirm handover |

### Notifications

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/notifications/` | Any role | List notifications |
| GET | `/notifications/unread-count` | Any role | Sidebar unread count |
| POST | `/notifications/mark-read` | Any role | Mark one notification as read |
| POST | `/notifications/mark-all-read` | Any role | Mark all notifications as read |
| DELETE | `/notifications/{id}` | Any role | Delete one notification |
| DELETE | `/notifications/` | Any role | Delete all notifications |

### Reports

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/reports/summary` | Admin+ | Report KPI summary |
| GET | `/reports/by-category` | Admin+ | Loans grouped by category |
| GET | `/reports/top-items` | Admin+ | Most borrowed items |
| GET | `/reports/loan-timeline` | Admin+ | Loan activity timeline |
| GET | `/reports/overdue-list` | Admin+ | Currently overdue loans |
| GET | `/reports/inventory-status` | Admin+ | Inventory status totals |
| GET | `/reports/user-activity` | Admin+ | User activity rankings |

### User Management

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/users/` | SuperAdmin | List users |
| POST | `/admin/users/` | SuperAdmin | Create user |
| GET | `/admin/users/{id}` | SuperAdmin | Get user |
| PUT | `/admin/users/{id}` | SuperAdmin | Update user |
| DELETE | `/admin/users/{id}` | SuperAdmin | Delete user |

---

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite, bcrypt
- Sessions: in-memory session tokens with HTTP-only cookie
- Frontend: vanilla HTML, CSS, and JavaScript served by FastAPI
- Theme: light/dark mode using the `data-theme` attribute and localStorage key `theme`

---

## Notes For Future Work

- Add proper automated tests for API behavior and role permissions.
- Consider moving repeated sidebar/theme code into reusable templates if the app grows.
- Add PDF generation for handovers and scheduled reports.
- Add real email delivery for reminders, overdue alerts, and digests.
