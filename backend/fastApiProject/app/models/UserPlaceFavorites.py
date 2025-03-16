from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import get_settings
from models.PlacePost import Base, get_db

class UserPlaceFavorites(Base):
    __tablename__ = "user_place_favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), index=True, nullable=False)
    place_id = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Create indexes for common queries
    __table_args__ = (
        Index('idx_user_place', user_id, place_id),
        Index('idx_created_at', created_at),
    )