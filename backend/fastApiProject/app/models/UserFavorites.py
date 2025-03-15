from sqlalchemy import Column, Integer, String, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import get_settings
from models.PlacePost import Base, get_db

class UserFavorites(Base):
    __tablename__ = "user_favorites"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), index=True)
    post_id = Column(String(32), index=True)
    
    # Create a unique constraint to prevent duplicate favorites
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uix_user_post'),
    )