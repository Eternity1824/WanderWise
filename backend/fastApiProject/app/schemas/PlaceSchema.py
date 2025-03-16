from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PlaceBase(BaseModel):
    place_id: str
    name: str
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    types: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    types: Optional[str] = None

class Place(PlaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PlaceWithPosts(Place):
    posts_count: int
    
    model_config = ConfigDict(from_attributes=True)