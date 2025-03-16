from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class PostBase(BaseModel):
    note_id: str
    user_id: str
    title: str
    content: Optional[str] = None
    tags: Optional[str] = None

class PostCreate(PostBase):
    images: Optional[List[str]] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    images: Optional[List[str]] = None
    is_published: Optional[bool] = None

class Post(PostBase):
    id: int
    images: Optional[Any] = None  # JSON field
    score: int
    view_count: int
    like_count: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostWithPlaces(Post):
    places: List[str]  # List of place_ids associated with this post
    
    model_config = ConfigDict(from_attributes=True)