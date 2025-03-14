from pydantic import BaseModel
from typing import Optional


class PlaceNoteBase(BaseModel):
    place_id: str
    note_id: str


class PlaceNoteCreate(PlaceNoteBase):
    pass


class PlaceNote(PlaceNoteBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True