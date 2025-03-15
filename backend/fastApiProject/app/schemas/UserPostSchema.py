from pydantic import BaseModel
from typing import Optional

class UserPostBase(BaseModel):
    post_id: str
    user_id: str

class UserPostCreate(UserPostBase):
    pass

class UserPost(UserPostBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True