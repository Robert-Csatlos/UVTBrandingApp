from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from fastapi import HTTPException
from . import models, schemas
from .auth import get_password_hash
import datetime


# --- Inventory ---

CONDITION_SUFFIXES = {
    "new": "N",
    "good": "G",
    "worn": "W",
}

CONDITION_ALIASES = {
    "n": "new",
    "new": "new",
    "nou": "new",
    "excellent": "new",
    "excelenta": "new",
    "excelentă": "new",
    "g": "good",
    "good": "good",
    "bun": "good",
    "buna": "good",
    "bună": "good",
    "w": "worn",
    "worn": "worn",
    "damaged": "worn",
    "worn/damaged": "worn",
    "uzat": "worn",
    "uzata": "worn",
    "uzată": "worn",
}


def normalize_condition(condition) -> str:
    raw = condition.value if hasattr(condition, "value") else condition
    key = str(raw or "").strip().lower()
    normalized = CONDITION_ALIASES.get(key)
    if not normalized:
        raise HTTPException(status_code=400, detail="Invalid condition")
    return normalized


def get_base_inventory_code(inventory_code: str) -> str:
    code = str(inventory_code or "").strip().upper()
    for suffix in CONDITION_SUFFIXES.values():
        marker = f"-{suffix}"
        if code.endswith(marker):
            return code[: -len(marker)]
    return code


def get_variant_inventory_code(inventory_code: str, condition: str) -> str:
    status = normalize_condition(condition)
    return f"{get_base_inventory_code(inventory_code)}-{CONDITION_SUFFIXES[status]}"


def get_condition_variant(db: Session, source_item: models.Inventory, condition: str):
    variant_code = get_variant_inventory_code(source_item.inventory_code, condition)
    return db.query(models.Inventory).filter(models.Inventory.inventory_code == variant_code).first()


def get_or_create_condition_variant(db: Session, source_item: models.Inventory, condition: str):
    status = normalize_condition(condition)
    variant = get_condition_variant(db, source_item, status)
    if variant:
        return variant

    variant = models.Inventory(
        name=source_item.name,
        category=source_item.category,
        inventory_code=get_variant_inventory_code(source_item.inventory_code, status),
        quantity=0,
        status=status,
        location=source_item.location,
        responsible_person=source_item.responsible_person,
        photo_path=source_item.photo_path,
        qr_code_path="pending.png",
    )
    db.add(variant)
    db.flush()
    return variant


def migrate_inventory_variant_codes(db: Session):
    items = db.query(models.Inventory).all()
    changed = False
    for item in items:
        target_code = get_variant_inventory_code(item.inventory_code, item.status)
        if item.inventory_code == target_code:
            continue
        existing = db.query(models.Inventory).filter(
            models.Inventory.inventory_code == target_code,
            models.Inventory.id != item.id,
        ).first()
        if existing:
            continue
        item.inventory_code = target_code
        changed = True
    if changed:
        db.commit()


def create_inventory(db: Session, item: schemas.InventoryCreate):
    data = item.model_dump()
    data["status"] = normalize_condition(data["status"])
    data["inventory_code"] = get_variant_inventory_code(data["inventory_code"], data["status"])

    existing = db.query(models.Inventory).filter(
        models.Inventory.inventory_code == data["inventory_code"]
    ).first()
    if existing:
        existing.name = data["name"]
        existing.category = data["category"]
        existing.quantity += data["quantity"]
        existing.status = data["status"]
        existing.location = data["location"]
        existing.responsible_person = data["responsible_person"]
        db.commit()
        db.refresh(existing)
        return existing

    db_item = models.Inventory(**data, photo_path="pending.jpg", qr_code_path="pending.png")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_all_inventory(db: Session):
    return db.query(models.Inventory).all()


def get_inventory_by_id(db: Session, item_id: int):
    return db.query(models.Inventory).filter(models.Inventory.id == item_id).first()


def update_inventory(db: Session, item_id: int, update: schemas.InventoryUpdate):
    item = get_inventory_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    data = update.model_dump(exclude_none=True)
    if "status" in data:
        data["status"] = normalize_condition(data["status"])
    target_status = data.get("status", item.status)
    target_code_source = data.get("inventory_code", item.inventory_code)
    if "status" in data or "inventory_code" in data:
        data["inventory_code"] = get_variant_inventory_code(target_code_source, target_status)
        existing = db.query(models.Inventory).filter(
            models.Inventory.inventory_code == data["inventory_code"],
            models.Inventory.id != item_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="That condition variant already exists")

    for field, value in data.items():
        setattr(item, field, value if not hasattr(value, "value") else value.value)
    db.commit()
    db.refresh(item)
    return item


def delete_inventory(db: Session, item_id: int):
    item = get_inventory_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


# --- Users ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role.value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        existing = get_user_by_email(db, user_update.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        db_user.email = user_update.email
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.role is not None:
        db_user.role = user_update.role.value
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()


# --- Stats ---

def get_stats(db: Session):
    now = datetime.datetime.utcnow()
    soon = now + datetime.timedelta(days=3)

    # Total units across all inventory items
    total = db.query(func.sum(models.Inventory.quantity)).scalar() or 0

    borrowed = db.query(models.Loan).filter(models.Loan.status == "active").count()
    overdue = db.query(models.Loan).filter(
        models.Loan.status == "active",
        models.Loan.deadline_date < now,
    ).count()
    pending = db.query(models.Loan).filter(
        models.Loan.status == "active",
        models.Loan.deadline_date >= now,
        models.Loan.deadline_date <= soon,
    ).count()
    low_stock = db.query(models.Inventory).filter(models.Inventory.quantity < 20).count()

    # Available = total units minus units currently on active loans
    loaned_units = db.query(func.sum(models.Loan.quantity)).filter(
        models.Loan.status == "active"
    ).scalar() or 0
    available = total - loaned_units

    return {
        "total": total,
        "available": available,
        "borrowed": borrowed,
        "overdue": overdue,
        "pending": pending,
        "low_stock": low_stock,
    }


# --- Loans ---

def create_loan(db: Session, loan: schemas.LoanCreate, borrower_id: int | None = None):
    from .notifications import create_notification, notify_all_admins

    if borrower_id is not None:
        loan = loan.model_copy(update={"user_id": borrower_id})

    item = get_inventory_by_id(db, loan.inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    borrower = get_user_by_id(db, loan.user_id)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    if item.quantity < loan.quantity:
        raise HTTPException(status_code=400, detail=f"Only {item.quantity} units available")

    loan = loan.model_copy(update={"condition_checkout": normalize_condition(item.status)})

    # Deduct stock
    item.quantity -= loan.quantity

    db_loan = models.Loan(**loan.model_dump(exclude_none=True))
    db.add(db_loan)
    db.flush()  # populate db_loan.id before notifications

    borrower_name = borrower.full_name or borrower.email
    deadline_str = loan.deadline_date.strftime("%d %b %Y")

    # Notify borrower: loan confirmed
    create_notification(
        db,
        recipient_id=loan.user_id,
        type="loan_made",
        title="📦 Loan Confirmed",
        message=f'Your loan of "{item.name}" (×{loan.quantity}) has been registered. Please return it by {deadline_str}.',
        loan_id=db_loan.id,
        inventory_id=item.id,
    )

    # Notify all Admins/SuperAdmins: new loan
    notify_all_admins(
        db,
        type="loan_made",
        title="📦 New Loan Registered",
        message=f'{borrower_name} loaned "{item.name}" (×{loan.quantity}). Due: {deadline_str}.',
        sender_id=loan.user_id,
        loan_id=db_loan.id,
        inventory_id=item.id,
    )

    # Low stock warning
    if item.quantity < 20:
        notify_all_admins(
            db,
            type="low_stock",
            title="📉 Low Stock Alert",
            message=f'"{item.name}" now has only {item.quantity} unit{"s" if item.quantity != 1 else ""} remaining.',
            inventory_id=item.id,
        )

    db.commit()
    db.refresh(db_loan)
    return db_loan


def get_all_loans(db: Session):
    """Return all loans with joined inventory and user info."""
    rows = (
        db.query(
            models.Loan,
            models.Inventory.name.label("item_name"),
            models.Inventory.inventory_code,
            models.User.full_name.label("borrower_name"),
            models.User.email.label("borrower_email"),
        )
        .join(models.Inventory, models.Loan.inventory_id == models.Inventory.id)
        .join(models.User, models.Loan.user_id == models.User.id)
        .order_by(models.Loan.checkout_date.desc())
        .all()
    )

    result = []
    for loan, item_name, inventory_code, borrower_name, borrower_email in rows:
        d = {c.name: getattr(loan, c.name) for c in loan.__table__.columns}
        d["item_name"] = item_name
        d["inventory_code"] = inventory_code
        d["borrower_name"] = borrower_name
        d["borrower_email"] = borrower_email
        result.append(d)
    return result


def return_loan(db: Session, loan_id: int, photo_checkin: str, condition_checkin: str):
    from .notifications import create_notification, notify_all_admins

    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == "returned":
        raise HTTPException(status_code=400, detail="Loan already returned")
    if not photo_checkin:
        raise HTTPException(status_code=400, detail="Return photo is required")
    if not condition_checkin:
        raise HTTPException(status_code=400, detail="Return condition is required")

    loan.status = "returned"
    loan.checkin_date = datetime.datetime.now(datetime.timezone.utc)
    loan.photo_checkin = photo_checkin
    item = get_inventory_by_id(db, loan.inventory_id)
    return_condition = normalize_condition(condition_checkin)
    checkout_condition = normalize_condition(loan.condition_checkout or (item.status if item else None))
    loan.condition_checkin = return_condition
    condition_changed = checkout_condition != return_condition
    if condition_changed:
        loan.is_deteriorated = True

    # Restore stock to the condition variant that was actually returned.
    if item:
        returned_variant = get_or_create_condition_variant(db, item, return_condition)
        returned_variant.quantity += loan.quantity

    item_name = item.name if item else f"Item #{loan.inventory_id}"
    borrower = get_user_by_id(db, loan.user_id)
    borrower_name = borrower.full_name or borrower.email if borrower else f"User #{loan.user_id}"

    # Notify borrower: return confirmed
    create_notification(
        db,
        recipient_id=loan.user_id,
        type="returned",
        title="✅ Return Confirmed",
        message=f'Your return of "{item_name}" (×{loan.quantity}) has been recorded. Thank you!',
        loan_id=loan.id,
        inventory_id=loan.inventory_id,
    )

    if condition_changed:
        notify_all_admins(
            db,
            type="deteriorated",
            title="Item Condition Changed",
            message=f'"{item_name}" from loan #{loan.id} was returned with condition "{return_condition}" after checkout condition "{checkout_condition}" (borrower: {borrower_name}).',
            loan_id=loan.id,
            inventory_id=loan.inventory_id,
        )

    db.commit()
    db.refresh(loan)
    return loan


def mark_loan_deteriorated(db: Session, loan_id: int, admin_id: int):
    from .notifications import notify_all_admins

    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.is_deteriorated:
        raise HTTPException(status_code=400, detail="Already marked as deteriorated")

    loan.is_deteriorated = True

    item = get_inventory_by_id(db, loan.inventory_id)
    borrower = get_user_by_id(db, loan.user_id)
    item_name = item.name if item else f"Item #{loan.inventory_id}"
    borrower_name = borrower.full_name or borrower.email if borrower else f"User #{loan.user_id}"

    notify_all_admins(
        db,
        type="deteriorated",
        title="⚠️ Item Flagged as Deteriorated",
        message=f'"{item_name}" from loan #{loan.id} (borrower: {borrower_name}) has been flagged as deteriorated.',
        sender_id=admin_id,
        loan_id=loan.id,
        inventory_id=loan.inventory_id,
    )

    db.commit()
    db.refresh(loan)
    return loan


# --- Handovers ---

def create_handover(db: Session, handover: schemas.HandoverCreate, sender_id: int):
    from .notifications import create_notification
    if handover.receiver_id == sender_id:
        raise HTTPException(status_code=400, detail="Sender and receiver must be different")

    db_handover = models.Handover(
        inventory_id=handover.inventory_id,
        sender_id=sender_id,
        receiver_id=handover.receiver_id,
        quantity=handover.quantity,
        condition_before=handover.condition_before,
        photo_before=handover.photo_before,
        notes=handover.notes,
        sender_signature_path=handover.sender_signature_path,
        status="pending",
    )
    db.add(db_handover)
    db.flush()

    item = get_inventory_by_id(db, handover.inventory_id)
    sender = get_user_by_id(db, sender_id)
    item_name = item.name if item else f"Item #{handover.inventory_id}"
    sender_name = sender.full_name or sender.email if sender else f"User #{sender_id}"

    create_notification(
        db,
        recipient_id=handover.receiver_id,
        sender_id=sender_id,
        type="manual",
        title="🔄 Handover Awaiting Your Confirmation",
        message=f'{sender_name} has initiated a handover of "{item_name}" (×{handover.quantity}) to you. Please confirm receipt.',
    )

    db.commit()
    db.refresh(db_handover)
    return db_handover


def get_all_handovers(db: Session):
    sender_alias = aliased(models.User)
    receiver_alias = aliased(models.User)

    rows = (
        db.query(
            models.Handover,
            models.Inventory.name.label("item_name"),
            models.Inventory.inventory_code,
            sender_alias.full_name.label("sender_name"),
            sender_alias.email.label("sender_email"),
            receiver_alias.full_name.label("receiver_name"),
            receiver_alias.email.label("receiver_email"),
        )
        .join(models.Inventory, models.Handover.inventory_id == models.Inventory.id)
        .join(sender_alias, models.Handover.sender_id == sender_alias.id)
        .join(receiver_alias, models.Handover.receiver_id == receiver_alias.id)
        .order_by(models.Handover.handover_date.desc())
        .all()
    )

    result = []
    for handover, item_name, inventory_code, sender_name, sender_email, receiver_name, receiver_email in rows:
        d = {c.name: getattr(handover, c.name) for c in handover.__table__.columns}
        d["item_name"] = item_name
        d["inventory_code"] = inventory_code
        d["sender_name"] = sender_name
        d["sender_email"] = sender_email
        d["receiver_name"] = receiver_name
        d["receiver_email"] = receiver_email
        result.append(d)
    return result


def confirm_handover(db: Session, handover_id: int, receiver_id: int, body: schemas.HandoverConfirm):
    handover = db.query(models.Handover).filter(models.Handover.id == handover_id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found")
    if handover.status == "completed":
        raise HTTPException(status_code=400, detail="Handover already completed")
    if handover.receiver_id != receiver_id:
        raise HTTPException(status_code=403, detail="Only the assigned receiver can confirm this handover")

    handover.status = "completed"
    handover.condition_after = body.condition_after
    handover.photo_after = body.photo_after
    handover.receiver_signature_path = body.receiver_signature_path

    db.commit()
    db.refresh(handover)
    return handover


def send_manual_notification(db: Session, loan_id: int, message: str, sender_id: int):
    from .notifications import create_notification

    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    sender = get_user_by_id(db, sender_id)
    sender_name = sender.full_name or sender.email if sender else "Admin"

    create_notification(
        db,
        recipient_id=loan.user_id,
        sender_id=sender_id,
        type="manual",
        title=f"📨 Message from {sender_name}",
        message=message,
        loan_id=loan.id,
        inventory_id=loan.inventory_id,
    )

    db.commit()
    return {"message": "Notification sent"}
