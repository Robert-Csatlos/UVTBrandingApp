from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

# Inventory Logic
def create_inventory(db: Session, item: schemas.InventoryCreate):
    db_item = models.Inventory(**item.model_dump(), photo_path="pending.jpg", qr_code_path="pending.png")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_all_inventory(db: Session):
    return db.query(models.Inventory).all()

# User Logic
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, hashed_password=get_password_hash(user.password), role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Loan Logic
def create_loan(db: Session, loan: schemas.LoanCreate):
    db_loan = models.Loan(**loan.model_dump())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan