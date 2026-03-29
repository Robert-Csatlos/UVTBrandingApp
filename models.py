from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from database import Base
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
    role = Column(String, default="Vizualizator") # Super Admin, Admin Dept, Coordinator, Vizualizator 

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    checkout_date = Column(DateTime, default=datetime.datetime.utcnow)
    # Deadline is usually event_date + 2 days 
    deadline_date = Column(DateTime, nullable=False) 
    checkin_date = Column(DateTime, nullable=True)
    photo_checkout = Column(String, nullable=False) # Mandatory proof 
    photo_checkin = Column(String, nullable=True)
    status = Column(String, default="active") # active, returned, overdue

class Handover(Base):
    __tablename__ = "handovers"
    __tablename__ = "handovers"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    signature_path = Column(String, nullable=False) # Digital signature
    pdf_report_path = Column(String, nullable=True) # Generated "Proces verbal" 
    is_confirmed = Column(Boolean, default=False)