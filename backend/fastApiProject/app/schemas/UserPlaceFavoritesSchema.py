from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class UserPlaceFavoriteCreate(BaseModel):
    user_id: str
    place_id: str

class UserPlaceFavoriteResponse(BaseModel):
    id: int
    user_id: str
    place_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserPlaceFavoriteCount(BaseModel):
    place_id: str
    favorite_count: int
    last_favorited_at: datetime