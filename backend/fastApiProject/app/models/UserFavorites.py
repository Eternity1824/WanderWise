from sqlalchemy import Column, Integer, String, Index, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from config import get_settings
from models.PlacePost import Base, get_db

class UserFavorites(Base):
    __tablename__ = "user_favorites"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), index=True)
    post_id = Column(String(32), ForeignKey("posts.note_id"), index=True)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    post = relationship("Post", foreign_keys=[post_id])
    
    # Create a unique constraint to prevent duplicate favorites
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uix_user_post'),
    )