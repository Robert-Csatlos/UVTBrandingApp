from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from .database import Base
import datetime


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    inventory_code = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Integer, default=0)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)
    responsible_person = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    qr_code_path = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False) # Must be @e-uvt.ro
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="vizualizator") # Super Admin, Admin Dept, Coordinator, Vizualizator

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, default=1)
    reason = Column(String, nullable=True) # eveniment / departament / service
    event_date = Column(DateTime, nullable=True) # deadline = event_date + 2 days
    checkout_date = Column(DateTime, default=lambda:datetime.datetime.now(datetime.timezone.utc))
    deadline_date = Column(DateTime, nullable=False)
    checkin_date = Column(DateTime, nullable=True)
    condition_checkout = Column(String, nullable=True) # excelentă / bună / uzată
    condition_checkin = Column(String, nullable=True)
    photo_checkout = Column(String, nullable=False) # Mandatory proof
    photo_checkin = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    accessories = Column(String, nullable=True)
    is_deteriorated = Column(Boolean, default=False)
    status = Column(String, default="active") # active, returned, overdue

class Handover(Base):
    __tablename__ = "handovers"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, default=1)
    handover_date = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    condition_before = Column(String, nullable=True) # sender's reported condition
    condition_after = Column(String, nullable=True) # receiver's reported condition
    photo_before = Column(String, nullable=True)
    photo_after = Column(String, nullable=True)
    notes = Column(String, nullable=True) # raportare diferențe
    sender_signature_path = Column(String, nullable=False)
    receiver_signature_path = Column(String, nullable=True)
    pdf_report_path = Column(String, nullable=True) # Generated "Proces verbal"
    status = Column(String, default="pending") # pending / completed