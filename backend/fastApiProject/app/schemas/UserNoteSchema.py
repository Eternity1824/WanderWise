from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserNoteBase(BaseModel):
    user_id: str
    post_count: int

class UserNoteCreate(UserNoteBase):
    pass

class UserNote(UserNoteBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)