from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from models.PlacePost import Base, get_db

class Place(Base):
    """
    The Place model represents a physical location that users can favorite or create posts about.
    It corresponds with place_id in the PlacePost and UserPlaceFavorites junction tables.
    """
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    place_id = Column(String(50), unique=True, nullable=False, index=True, comment="Google Places ID or custom identifier")
    name = Column(String(255), nullable=False, index=True)
    formatted_address = Column(String(512), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    website = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    types = Column(String(255), nullable=True, comment="Comma-separated list of place types")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_place_location', latitude, longitude),
        Index('idx_place_name', name),
    )
    
    def __repr__(self):
        return f"<Place place_id='{self.place_id}' name='{self.name}'>"