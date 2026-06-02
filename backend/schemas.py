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
    overdue = "overdue"


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
    pass


class Inventory(InventoryBase):
    id: int
    photo_path: Optional[str] = None
    qr_code_path: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    inventory_code: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    status: Optional[InventoryStatus] = None
    location: Optional[str] = None
    responsible_person: Optional[str] = None


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
        if v <= datetime.now(tz=v.tzinfo):
            raise ValueError("Deadline must be in the future")
        return v


class LoanCreate(LoanBase):
    quantity: int = Field(ge=1, default=1)
    checkout_date: Optional[datetime] = None
    event_date: Optional[datetime] = None
    reason: Optional[str] = None
    condition_checkout: str
    photo_checkout: str = Field(min_length=1)
    notes: Optional[str] = None
    accessories: Optional[str] = None


class LoanReturn(BaseModel):
    condition_checkin: str
    photo_checkin: str = Field(min_length=1)
    notes: Optional[str] = None


class Loan(LoanBase):
    id: int
    quantity: int
    checkout_date: Optional[datetime] = None
    checkin_date: Optional[datetime] = None
    photo_checkout: str
    photo_checkin: Optional[str] = None
    condition_checkout: Optional[str] = None
    condition_checkin: Optional[str] = None
    notes: Optional[str] = None
    reason: Optional[str] = None
    event_date: Optional[datetime] = None
    accessories: Optional[str] = None
    is_deteriorated: bool = False
    status: LoanStatus

    class Config:
        from_attributes = True


# --- HANDOVER SCHEMAS ---

class HandoverCreate(BaseModel):
    inventory_id: int
    receiver_id: int
    quantity: int = Field(ge=1, default=1)
    condition_before: Optional[str] = None
    photo_before: Optional[str] = None
    notes: Optional[str] = None
    sender_signature_path: str


class HandoverConfirm(BaseModel):
    condition_after: Optional[str] = None
    photo_after: Optional[str] = None
    receiver_signature_path: str


class HandoverOut(BaseModel):
    id: int
    inventory_id: int
    sender_id: int
    receiver_id: int
    quantity: int
    handover_date: Optional[datetime] = None
    condition_before: Optional[str] = None
    condition_after: Optional[str] = None
    photo_before: Optional[str] = None
    photo_after: Optional[str] = None
    notes: Optional[str] = None
    sender_signature_path: str
    receiver_signature_path: Optional[str] = None
    status: str
    item_name: Optional[str] = None
    inventory_code: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_email: Optional[str] = None

    class Config:
        from_attributes = True
