"""
loans.py  –  All loan-related API routes.

Mount this in api.py with:
    from .loans import router as loans_router
    app.include_router(loans_router)

Also add the page route:
    @app.get("/loans")
    def serve_loans(request: Request):
        if get_session_user_id(request) is None:
            return RedirectResponse(url="/", status_code=302)
        return FileResponse("frontend/html/loanTrackingDashboard.html")
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime

from . import models
from .database import get_db
from .auth import get_current_user, require_admin_or_above

router = APIRouter(prefix="/loans", tags=["loans"])


# ── Schemas (inline, kept close to the routes) ────────────────────────

class LoanReturnUpdate(BaseModel):
    condition_checkin: Optional[str] = None   # excellent / good / worn
    photo_checkin:     Optional[str] = None   # base64 or path
    notes:             Optional[str] = None


class LoanDeteriorateUpdate(BaseModel):
    notes: Optional[str] = None


class NotificationRequest(BaseModel):
    extra_note: Optional[str] = None


# ── Helper: enrich a loan with item + user info ───────────────────────

def _enrich(loan: models.Loan, db: Session) -> dict:
    item = db.query(models.Inventory).filter(models.Inventory.id == loan.inventory_id).first()
    user = db.query(models.User).filter(models.User.id == loan.user_id).first()

    # Auto-mark overdue
    now = datetime.datetime.utcnow()
    if loan.status == "active" and loan.deadline_date and loan.deadline_date < now:
        loan.status = "overdue"
        db.commit()

    return {
        "id":               loan.id,
        "inventory_id":     loan.inventory_id,
        "user_id":          loan.user_id,
        "quantity":         loan.quantity,
        "reason":           loan.reason,
        "checkout_date":    loan.checkout_date.isoformat()  if loan.checkout_date  else None,
        "deadline_date":    loan.deadline_date.isoformat()  if loan.deadline_date  else None,
        "checkin_date":     loan.checkin_date.isoformat()   if loan.checkin_date   else None,
        "condition_checkout": loan.condition_checkout,
        "condition_checkin":  loan.condition_checkin,
        "photo_checkout":   loan.photo_checkout,
        "photo_checkin":    loan.photo_checkin,
        "notes":            loan.notes,
        "accessories":      loan.accessories,
        "is_deteriorated":  loan.is_deteriorated,
        "status":           loan.status,
        # enriched
        "item_name":        item.name              if item else None,
        "item_code":        item.inventory_code    if item else None,
        "borrower_name":    user.full_name         if user else None,
        "borrower_email":   user.email             if user else None,
    }


# ── Routes ────────────────────────────────────────────────────────────

@router.get("/")
def list_loans(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Return all loans, enriched with item + borrower info. Visible to everyone."""
    loans = db.query(models.Loan).order_by(models.Loan.id.desc()).all()
    return [_enrich(l, db) for l in loans]


@router.get("/{loan_id}")
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return _enrich(loan, db)


@router.put("/{loan_id}/return")
def mark_returned(
    loan_id: int,
    body: LoanReturnUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """Mark a loan as returned. Admin/SuperAdmin only."""
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == "returned":
        raise HTTPException(status_code=400, detail="Loan is already marked as returned")

    loan.status           = "returned"
    loan.checkin_date     = datetime.datetime.utcnow()
    loan.condition_checkin = body.condition_checkin
    if body.photo_checkin:
        loan.photo_checkin = body.photo_checkin
    if body.notes:
        existing = loan.notes or ""
        loan.notes = f"{existing}\n[Return note] {body.notes}".strip()

    db.commit()
    db.refresh(loan)
    return _enrich(loan, db)


@router.put("/{loan_id}/deteriorate")
def mark_deteriorated(
    loan_id: int,
    body: LoanDeteriorateUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """Flag a loan's item as deteriorated. Admin/SuperAdmin only."""
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan.is_deteriorated = True
    if body.notes:
        existing = loan.notes or ""
        loan.notes = f"{existing}\n[Deterioration] {body.notes}".strip()

    db.commit()
    db.refresh(loan)
    return _enrich(loan, db)


@router.post("/{loan_id}/notify")
def send_notification(
    loan_id: int,
    body: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_above),
):
    """
    Record a deadline notification for this loan.
    Admin/SuperAdmin only.

    Currently stores the notification as a note on the loan and returns
    the generated message. You can extend this to email / push later.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    item = db.query(models.Inventory).filter(models.Inventory.id == loan.inventory_id).first()
    user = db.query(models.User).filter(models.User.id == loan.user_id).first()

    now      = datetime.datetime.utcnow()
    overdue  = loan.deadline_date and loan.deadline_date < now
    deadline = loan.deadline_date.strftime("%d %b %Y") if loan.deadline_date else "—"
    item_name = item.name if item else f"Item #{loan.inventory_id}"

    if overdue:
        message = (
            f"⚠️ Overdue reminder: the loan for '{item_name}' was due on {deadline} "
            f"and is now overdue. Please return the item immediately."
        )
    else:
        message = (
            f"🔔 Deadline reminder: the loan for '{item_name}' is due on {deadline}. "
            f"Please ensure the item is returned on time."
        )

    if body.extra_note:
        message += f"\n\n{body.extra_note}"

    # Append notification log to the loan's notes field
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    note_line = f"[Notification sent {timestamp} by {current_user.full_name or current_user.email}]"
    loan.notes = f"{loan.notes or ''}\n{note_line}".strip()
    db.commit()

    return {
        "message": "Notification recorded",
        "recipient_email": user.email if user else None,
        "notification_text": message,
    }