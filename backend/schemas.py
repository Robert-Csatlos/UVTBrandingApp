from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


# --- ENUMS ---

class InventoryStatus(str, Enum):
    new = "new"
    good = "good"
    worn = "worn"


class UserRole(str, Enum):
    superadmin = "SuperAdmin"
    admin = "Admin"
    coordinator = "Coordinator"
    vizualizator = "Vizualizator"


class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    late = "late"


# --- INVENTORY SCHEMAS ---

class InventoryBase(BaseModel):
    name: str
    category: str
    inventory_code: str
    quantity: int = Field(ge=0)
    status: InventoryStatus
    location: str
    responsible_person: str


class InventoryCreate(InventoryBase):
    pass  # No extra validation needed anymore


class Inventory(InventoryBase):
    id: int
    photo_path: Optional[str] = None
    qr_code_path: Optional[str] = None

    class Config:
        from_attributes = True


# --- USER SCHEMAS ---

class UserBase(BaseModel):
    email: EmailStr

    @field_validator('email')
    @classmethod
    def validate_uvt_email(cls, v: str):
        if not v.endswith("@e-uvt.ro"):
            raise ValueError("Email must be a valid @e-uvt.ro address")
        return v


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.vizualizator
    full_name: str


class User(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)

    @field_validator("email")
    @classmethod
    def validate_uvt_email(cls, v: str):
        if v is not None and not v.endswith("@e-uvt.ro"):
            raise ValueError("Email must be a valid @e-uvt.ro address")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- LOAN SCHEMAS ---

class LoanBase(BaseModel):
    inventory_id: int
    user_id: int
    deadline_date: datetime

    @field_validator("deadline_date")
    @classmethod
    def validate_deadline(cls, v: datetime):
        if v <= datetime.now():
            raise ValueError("Deadline must be in the future")
        return v


class LoanCreate(LoanBase):
    photo_checkout: str  # path or base64


class Loan(LoanBase):
    id: int
    checkout_date: datetime
    checkin_date: Optional[datetime] = None
    photo_checkout: str
    photo_checkin: Optional[str] = None
    status: LoanStatus

    class Config:
        from_attributes = True


# --- HANDOVER SCHEMAS ---

class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    inventory_code: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    status: Optional[InventoryStatus] = None
    location: Optional[str] = None
    responsible_person: Optional[str] = None


class HandoverCreate(BaseModel):
    inventory_id: int
    sender_id: int
    receiver_id: int
    signature_path: str

    @field_validator("receiver_id")
    @classmethod
    def validate_users(cls, v, values):
        if "sender_id" in values and v == values["sender_id"]:
            raise ValueError("Sender and receiver must be different")
        return v


class Handover(HandoverCreate):
    id: int
    pdf_report_path: Optional[str] = None
    is_confirmed: bool = False

    class Config:
        from_attributes = True