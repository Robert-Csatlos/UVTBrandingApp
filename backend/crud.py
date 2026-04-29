from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from .auth import get_password_hash


# --- Inventory ---

def create_inventory(db: Session, item: schemas.InventoryCreate):
    db_item = models.Inventory(**item.model_dump(), photo_path="pending.jpg", qr_code_path="pending.png")
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
    for field, value in update.model_dump(exclude_none=True).items():
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


# --- Loans ---

def create_loan(db: Session, loan: schemas.LoanCreate):
    db_loan = models.Loan(**loan.model_dump())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan
