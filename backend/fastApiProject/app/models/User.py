from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.PlacePost import Base, get_db

class User(Base):
    """
    The User model represents application users who can create posts and favorite places.
    It corresponds with user_id in the UserNote, UserFavorites, and UserPlaceFavorites tables.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    notes = relationship("UserNote", back_populates="user")
    favorites = relationship("UserFavorites", back_populates="user")
    place_favorites = relationship("UserPlaceFavorites", back_populates="user")
    posts = relationship("Post", primaryjoin="User.user_id == Post.user_id", foreign_keys="Post.user_id", viewonly=True)
    
    __table_args__ = (
        Index('idx_user_active', is_active),
        Index('idx_user_username', username),
    )
    
    def __repr__(self):
        return f"<User user_id='{self.user_id}' username='{self.username}'>"