from pydantic import BaseModel
from typing import Optional, List

class UserFavoriteBase(BaseModel):
    post_id: str
    user_id: str

class UserFavoriteCreate(UserFavoriteBase):
    pass

class UserFavorite(UserFavoriteBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

class UserFavoritesList(BaseModel):
    favorites: List[UserFavorite]