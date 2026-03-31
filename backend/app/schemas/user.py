from pydantic import BaseModel, EmailStr
from typing import Optional

class PreferenceBase(BaseModel):
    sleep_pref: Optional[str] = None
    sleep_sense: Optional[str] = None
    personality: Optional[str] = None
    living_habit: Optional[str] = None
    noise_tolerance: Optional[str] = None
    guest_policy: Optional[str] = None

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None

class UserCreate(UserBase):
    password: str
    preferences: Optional[PreferenceCreate] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    preferences: Optional[PreferenceCreate] = None

class UserResponse(UserBase):
    id: int
    verification_status: bool
    preference: Optional[PreferenceResponse]

    class Config:
        from_attributes = True
