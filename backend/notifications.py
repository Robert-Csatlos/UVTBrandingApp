"""
notifications.py
────────────────
Router for the Notification system.

Automatic notifications are fired from crud.py whenever:
  - A loan is created        → notify all Admins/SuperAdmins ("Loan made")
                             → notify the borrower ("Loan confirmed")
  - A loan goes overdue      → notify borrower ("Overdue!")
                             → notify all Admins/SuperAdmins ("Overdue loan for X")
  - A loan is returned       → notify the borrower ("Return confirmed")
  - An item is deteriorated  → notify all Admins/SuperAdmins
  - Quantity drops < 20      → notify all Admins/SuperAdmins ("Low stock")

Manual notifications are sent by Admins/SuperAdmins via POST /loans/{id}/notify
and go to the borrower of that loan.

A background scheduler runs every hour and:
  - Creates "due_soon" notifications about 1 day before the deadline (once per loan)
  - Creates "overdue" notifications for newly overdue loans (once per loan)
  - Creates a Monday morning active-loans digest for operators
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from . import models
from .database import get_db
from .auth import get_current_user, require_admin_or_above
import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime.datetime
    loan_id: Optional[int] = None
    inventory_id: Optional[int] = None
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True


class MarkReadBody(BaseModel):
    ids: list[int]


# ─── Helper: create a notification (called from crud.py and scheduler) ───────

def create_notification(
    db: Session,
    recipient_id: int,
    type: str,
    title: str,
    message: str,
    sender_id: Optional[int] = None,
    loan_id: Optional[int] = None,
    inventory_id: Optional[int] = None,
):
    notif = models.Notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        type=type,
        title=title,
        message=message,
        loan_id=loan_id,
        inventory_id=inventory_id,
    )
    db.add(notif)
    # Note: caller is responsible for db.commit()


def notify_all_admins(
    db: Session,
    type: str,
    title: str,
    message: str,
    sender_id: Optional[int] = None,
    loan_id: Optional[int] = None,
    inventory_id: Optional[int] = None,
):
    """Fire the same notification to every Admin and SuperAdmin."""
    admins = db.query(models.User).filter(
        models.User.role.in_(["SuperAdmin", "Admin"])
    ).all()
    for admin in admins:
        create_notification(
            db,
            recipient_id=admin.id,
            type=type,
            title=title,
            message=message,
            sender_id=sender_id,
            loan_id=loan_id,
            inventory_id=inventory_id,
        )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/", response_model=list[NotificationOut])
def list_my_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all notifications for the logged-in user, newest first."""
    q = db.query(models.Notification).filter(
        models.Notification.recipient_id == current_user.id
    )
    if unread_only:
        q = q.filter(models.Notification.is_read == False)
    notifications = q.order_by(models.Notification.created_at.desc()).all()

    result = []
    for n in notifications:
        sender_name = None
        if n.sender_id:
            sender = db.query(models.User).filter(models.User.id == n.sender_id).first()
            if sender:
                sender_name = sender.full_name or sender.email
        result.append(NotificationOut(
            id=n.id,
            type=n.type,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at,
            loan_id=n.loan_id,
            inventory_id=n.inventory_id,
            sender_name=sender_name,
        ))
    return result


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    count = db.query(func.count(models.Notification.id)).filter(
        models.Notification.recipient_id == current_user.id,
        models.Notification.is_read == False,
    ).scalar()
    return {"count": count or 0}


@router.post("/mark-read")
def mark_read(
    body: MarkReadBody,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mark specific notification IDs as read (must belong to current user)."""
    db.query(models.Notification).filter(
        models.Notification.id.in_(body.ids),
        models.Notification.recipient_id == current_user.id,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"marked": len(body.ids)}


@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.Notification).filter(
        models.Notification.recipient_id == current_user.id,
        models.Notification.is_read == False,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read"}


@router.delete("/{notif_id}")
def delete_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notif_id,
        models.Notification.recipient_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"message": "Deleted"}


@router.delete("/")
def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db.query(models.Notification).filter(
        models.Notification.recipient_id == current_user.id,
    ).delete(synchronize_session=False)
    db.commit()
    return {"message": "All notifications cleared"}


# ─── Scheduler: called on startup, runs hourly checks ────────────────────────

def run_scheduled_checks(db: Session):
    """
    Check for due-soon and overdue loans and create notifications if not
    already created. Uses the notification type + loan_id to deduplicate.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    reminder_start = now + datetime.timedelta(hours=23)
    reminder_end = now + datetime.timedelta(hours=25)

    # ── Due-soon (active loans with deadline within 3 days) ──
    due_soon_loans = db.query(models.Loan).filter(
        models.Loan.status == "active",
        models.Loan.deadline_date >= reminder_start,
        models.Loan.deadline_date <= reminder_end,
    ).all()

    for loan in due_soon_loans:
        # Only notify once per loan
        already = db.query(models.Notification).filter(
            models.Notification.loan_id == loan.id,
            models.Notification.type == "due_soon",
            models.Notification.recipient_id == loan.user_id,
        ).first()
        if already:
            continue

        item = db.query(models.Inventory).filter(models.Inventory.id == loan.inventory_id).first()
        item_name = item.name if item else f"Item #{loan.inventory_id}"
        create_notification(
            db,
            recipient_id=loan.user_id,
            type="due_soon",
            title="Return Due Tomorrow",
            message=f'"{item_name}" (x{loan.quantity}) is due back tomorrow. Please return it on time.',
            loan_id=loan.id,
            inventory_id=loan.inventory_id,
        )

    # ── Overdue (active loans past deadline) ──
    overdue_loans = db.query(models.Loan).filter(
        models.Loan.status == "active",
        models.Loan.deadline_date < now,
    ).all()

    for loan in overdue_loans:
        borrower = db.query(models.User).filter(models.User.id == loan.user_id).first()
        item = db.query(models.Inventory).filter(models.Inventory.id == loan.inventory_id).first()
        item_name = item.name if item else f"Item #{loan.inventory_id}"
        borrower_name = borrower.full_name or borrower.email if borrower else f"User #{loan.user_id}"

        deadline_aware = loan.deadline_date.replace(tzinfo=datetime.timezone.utc)
        days_late = (now - deadline_aware).days

        # Notify borrower (once per loan)
        already_borrower = db.query(models.Notification).filter(
            models.Notification.loan_id == loan.id,
            models.Notification.type == "overdue",
            models.Notification.recipient_id == loan.user_id,
        ).first()
        if not already_borrower:
            create_notification(
                db,
                recipient_id=loan.user_id,
                type="overdue",
                title="🚨 Overdue Return!",
                message=f'"{item_name}" (×{loan.quantity}) was due {days_late} day{"s" if days_late != 1 else ""} ago. Please return it immediately.',
                loan_id=loan.id,
                inventory_id=loan.inventory_id,
            )

        # Notify admins (once per loan)
        admins = db.query(models.User).filter(models.User.role.in_(["SuperAdmin", "Admin"])).all()
        for admin in admins:
            already_admin = db.query(models.Notification).filter(
                models.Notification.loan_id == loan.id,
                models.Notification.type == "overdue",
                models.Notification.recipient_id == admin.id,
            ).first()
            if not already_admin:
                create_notification(
                    db,
                    recipient_id=admin.id,
                    type="overdue",
                    title="Overdue Loan",
                    message=f'{borrower_name} has not returned "{item_name}" (x{loan.quantity}). Overdue by {days_late} day{"s" if days_late != 1 else ""}.',
                    loan_id=loan.id,
                    inventory_id=loan.inventory_id,
                )

    local_now = now.astimezone(ZoneInfo("Europe/Bucharest"))
    if local_now.weekday() == 0 and 8 <= local_now.hour < 10:
        local_day_start = datetime.datetime.combine(local_now.date(), datetime.time.min)
        active_rows = (
            db.query(
                models.Loan,
                models.Inventory.name,
                models.Inventory.inventory_code,
                models.User.full_name,
                models.User.email,
            )
            .join(models.Inventory, models.Loan.inventory_id == models.Inventory.id)
            .join(models.User, models.Loan.user_id == models.User.id)
            .filter(models.Loan.status == "active")
            .order_by(models.Loan.deadline_date.asc())
            .all()
        )

        if active_rows:
            lines = []
            for loan, item_name, code, borrower_name, borrower_email in active_rows[:8]:
                borrower = borrower_name or borrower_email
                due = loan.deadline_date.strftime("%d %b %Y") if loan.deadline_date else "no deadline"
                lines.append(f"- {item_name} ({code}) x{loan.quantity}, {borrower}, due {due}")
            if len(active_rows) > 8:
                lines.append(f"- plus {len(active_rows) - 8} more active loan(s)")

            operators = db.query(models.User).filter(
                models.User.role.in_(["SuperAdmin", "Admin", "Coordinator"])
            ).all()
            for user in operators:
                already_digest = db.query(models.Notification).filter(
                    models.Notification.recipient_id == user.id,
                    models.Notification.type == "weekly_digest",
                    models.Notification.created_at >= local_day_start,
                ).first()
                if already_digest:
                    continue
                create_notification(
                    db,
                    recipient_id=user.id,
                    type="weekly_digest",
                    title="Monday Active Loans Digest",
                    message="Active loans this week:\n" + "\n".join(lines),
                )

    db.commit()
