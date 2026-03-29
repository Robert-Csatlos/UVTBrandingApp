from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

# --- INVENTORY SCHEMAS ---
class InventoryBase(BaseModel):
    name: str
    category: str
    inventory_code: str
    quantity: int = Field(ge=0)
    status: str
    location: str
    responsible_person: str

class InventoryCreate(InventoryBase):
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str):
        allowed = ['new', 'good', 'worn']
        if v.lower() not in allowed:
            raise ValueError(f"Status must be: {', '.join(allowed)}")
        return v.lower()

class Inventory(InventoryBase):
    id: int
    photo_path: Optional[str]
    qr_code_path: Optional[str]
    class Config: from_attributes = True

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr # Validates format

class UserCreate(UserBase):
    password: str
    role: str = "Vizualizator"

    @field_validator('email')
    @classmethod
    def validate_uvt_email(cls, v: str):
        if not v.endswith("@e-uvt.ro"):
            raise ValueError("Email must be a valid @e-uvt.ro address")
        return v

class User(UserBase):
    id: int
    role: str
    class Config: from_attributes = True

# --- LOAN SCHEMAS ---
class LoanBase(BaseModel):
    inventory_id: int
    user_id: int
    deadline_date: datetime

class LoanCreate(LoanBase):
    photo_checkout: str # Mandatory path or base64

class Loan(LoanBase):
    id: int
    checkout_date: datetime
    checkin_date: Optional[datetime]
    photo_checkout: str
    photo_checkin: Optional[str]
    status: str
    class Config: from_attributes = True

# --- HANDOVER SCHEMAS ---
class HandoverCreate(BaseModel):
    inventory_id: int
    sender_id: int
    receiver_id: int
    signature_path: str

class Handover(HandoverCreate):
    id: int
    pdf_report_path: Optional[str]
    is_confirmed: bool
    class Config: from_attributes = True