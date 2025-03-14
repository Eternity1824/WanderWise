from pydantic import BaseModel
from typing import Optional


class PlaceNoteBase(BaseModel):
    place_id: str
    note_id: int


class PlaceNoteCreate(PlaceNoteBase):
    pass


class PlaceNote(PlaceNoteBase):
    class Config:
        orm_mode = True
        from_attributes = True