from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UserFavoriteBase(BaseModel):
    post_id: str
    user_id: str

class UserFavoriteCreate(UserFavoriteBase):
    pass

class UserFavorite(UserFavoriteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserFavoritesList(BaseModel):
    favorites: List[UserFavorite]