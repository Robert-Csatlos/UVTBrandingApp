from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from . import models
from .database import get_db
from .auth import require_admin_or_above
import datetime

router = APIRouter(prefix="/reports", tags=["reports"])


def _date_range(period: str):
    """Return (start, end) UTC datetimes for the given period."""
    now = datetime.datetime.utcnow()
    if period == "week":
        start = now - datetime.timedelta(days=7)
    elif period == "month":
        start = now - datetime.timedelta(days=30)
    elif period == "quarter":
        start = now - datetime.timedelta(days=90)
    elif period == "year":
        start = now - datetime.timedelta(days=365)
    else:  # "all"
        start = datetime.datetime(2000, 1, 1)
    return start, now


@router.get("/summary")
def get_summary(
    period: str = "month",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    High-level KPIs for the reports dashboard.
    """
    start, end = _date_range(period)

    total_items = db.query(models.Inventory).count()
    total_loans = db.query(models.Loan).filter(
        models.Loan.checkout_date >= start,
        models.Loan.checkout_date <= end,
    ).count()
    active_loans = db.query(models.Loan).filter(models.Loan.status == "active").count()
    returned_loans = db.query(models.Loan).filter(
        models.Loan.status == "returned",
        models.Loan.checkin_date >= start,
        models.Loan.checkin_date <= end,
    ).count()
    overdue_loans = db.query(models.Loan).filter(
        models.Loan.status == "active",
        models.Loan.deadline_date < end,
    ).count()
    deteriorated = db.query(models.Loan).filter(
        models.Loan.is_deteriorated == True,
        models.Loan.checkout_date >= start,
    ).count()
    total_users = db.query(models.User).count()
    low_stock = db.query(models.Inventory).filter(models.Inventory.quantity < 20).count()

    return {
        "total_items": total_items,
        "total_loans": total_loans,
        "active_loans": active_loans,
        "returned_loans": returned_loans,
        "overdue_loans": overdue_loans,
        "deteriorated_items": deteriorated,
        "total_users": total_users,
        "low_stock_items": low_stock,
    }


@router.get("/by-category")
def get_loans_by_category(
    period: str = "month",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    Loan counts grouped by inventory category, for the given period.
    """
    start, end = _date_range(period)

    rows = (
        db.query(models.Inventory.category, func.count(models.Loan.id).label("loan_count"))
        .join(models.Loan, models.Loan.inventory_id == models.Inventory.id)
        .filter(
            models.Loan.checkout_date >= start,
            models.Loan.checkout_date <= end,
        )
        .group_by(models.Inventory.category)
        .order_by(func.count(models.Loan.id).desc())
        .all()
    )

    return [{"category": r.category, "loan_count": r.loan_count} for r in rows]


@router.get("/top-items")
def get_top_items(
    period: str = "month",
    limit: int = 10,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    Most-borrowed inventory items in the given period.
    """
    start, end = _date_range(period)

    rows = (
        db.query(
            models.Inventory.id,
            models.Inventory.name,
            models.Inventory.category,
            models.Inventory.inventory_code,
            func.count(models.Loan.id).label("loan_count"),
        )
        .join(models.Loan, models.Loan.inventory_id == models.Inventory.id)
        .filter(
            models.Loan.checkout_date >= start,
            models.Loan.checkout_date <= end,
        )
        .group_by(models.Inventory.id)
        .order_by(func.count(models.Loan.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "inventory_code": r.inventory_code,
            "loan_count": r.loan_count,
        }
        for r in rows
    ]


@router.get("/loan-timeline")
def get_loan_timeline(
    period: str = "month",
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    Daily loan checkout counts for a sparkline / timeline chart.
    """
    start, end = _date_range(period)

    loans = (
        db.query(models.Loan.checkout_date)
        .filter(
            models.Loan.checkout_date >= start,
            models.Loan.checkout_date <= end,
        )
        .all()
    )

    # Bucket by day
    buckets: dict[str, int] = {}
    for (checkout_date,) in loans:
        if checkout_date:
            day = checkout_date.strftime("%Y-%m-%d")
            buckets[day] = buckets.get(day, 0) + 1

    # Fill gaps
    result = []
    cursor = start.date()
    while cursor <= end.date():
        key = cursor.strftime("%Y-%m-%d")
        result.append({"date": key, "count": buckets.get(key, 0)})
        cursor += datetime.timedelta(days=1)

    return result


@router.get("/overdue-list")
def get_overdue_list(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    All currently overdue loans with item and user info.
    """
    now = datetime.datetime.utcnow()

    rows = (
        db.query(
            models.Loan.id,
            models.Loan.deadline_date,
            models.Loan.checkout_date,
            models.Loan.quantity,
            models.Inventory.name.label("item_name"),
            models.Inventory.inventory_code,
            models.User.full_name.label("borrower_name"),
            models.User.email.label("borrower_email"),
        )
        .join(models.Inventory, models.Loan.inventory_id == models.Inventory.id)
        .join(models.User, models.Loan.user_id == models.User.id)
        .filter(
            models.Loan.status == "active",
            models.Loan.deadline_date < now,
        )
        .order_by(models.Loan.deadline_date.asc())
        .all()
    )

    return [
        {
            "loan_id": r.id,
            "item_name": r.item_name,
            "inventory_code": r.inventory_code,
            "borrower_name": r.borrower_name,
            "borrower_email": r.borrower_email,
            "quantity": r.quantity,
            "checkout_date": r.checkout_date.isoformat() if r.checkout_date else None,
            "deadline_date": r.deadline_date.isoformat() if r.deadline_date else None,
            "days_overdue": (now - r.deadline_date).days if r.deadline_date else None,
        }
        for r in rows
    ]


@router.get("/inventory-status")
def get_inventory_status_breakdown(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    Count of inventory items by status (new / good / worn).
    """
    rows = (
        db.query(models.Inventory.status, func.count(models.Inventory.id).label("count"))
        .group_by(models.Inventory.status)
        .all()
    )
    return [{"status": r.status, "count": r.count} for r in rows]


@router.get("/user-activity")
def get_user_activity(
    period: str = "month",
    limit: int = 10,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin_or_above),
):
    """
    Most active borrowers in the given period.
    """
    start, end = _date_range(period)

    rows = (
        db.query(
            models.User.id,
            models.User.full_name,
            models.User.email,
            models.User.role,
            func.count(models.Loan.id).label("loan_count"),
        )
        .join(models.Loan, models.Loan.user_id == models.User.id)
        .filter(
            models.Loan.checkout_date >= start,
            models.Loan.checkout_date <= end,
        )
        .group_by(models.User.id)
        .order_by(func.count(models.Loan.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": r.id,
            "full_name": r.full_name,
            "email": r.email,
            "role": r.role,
            "loan_count": r.loan_count,
        }
        for r in rows
    ]
