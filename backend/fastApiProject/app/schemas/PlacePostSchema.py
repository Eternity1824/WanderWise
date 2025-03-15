from pydantic import BaseModel
from typing import Optional


class PlacePostBase(BaseModel):
    place_id: str
    note_id: str


class PlacePostCreate(PlacePostBase):
    pass


class PlacePost(PlacePostBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True