from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from models.PlacePost import Base, get_db

class Post(Base):
    """
    The Post model represents user-generated content about places.
    It corresponds with note_id in the PlacePost junction table.
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    images = Column(JSON, nullable=True, comment="JSON array of image URLs")
    tags = Column(String(255), nullable=True, comment="Comma-separated list of tags")
    score = Column(Integer, default=0, nullable=False, comment="Popularity or quality score")
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_post_user', user_id),
        Index('idx_post_tags', tags),
        Index('idx_post_search', title, content),
    )
    
    def __repr__(self):
        return f"<Post note_id='{self.note_id}' title='{self.title[:20]}...'>"