from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    
class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserWithStats(User):
    post_count: int
    favorite_count: int
    
    model_config = ConfigDict(from_attributes=True)