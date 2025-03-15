from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from config import get_settings
from models.PlacePost import Base, get_db

class UserNote(Base):
    __tablename__ = "user_notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), index=True)
    post_count = Column(Integer, default=0)  # Tracks the count of posts favorited by the user
    
    # Relationships
    user = relationship("User", back_populates="notes")