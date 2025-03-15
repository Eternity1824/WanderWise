from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.config import get_settings
from app.models.PlacePost import Base, get_db

class UserNote(Base):
    __tablename__ = "user_notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), index=True)
    post_count = Column(Integer, default=0)  # Tracks the count of posts favorited by the user