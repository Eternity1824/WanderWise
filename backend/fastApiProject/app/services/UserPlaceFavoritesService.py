from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.UserPlaceFavorites import UserPlaceFavorites
from models.PlacePost import get_db
from core.MySqlCore import MySqlCore
from schemas.UserPlaceFavoritesSchema import UserPlaceFavoriteCount

class UserPlaceFavoritesService:
    def __init__(self, db: Session):
        self.db = db
        self.core = MySqlCore(db, UserPlaceFavorites)
    
    def add_favorite(self, user_id: str, place_id: str) -> Optional[UserPlaceFavorites]:
        """
        Add a new favorite record for a user and place
        
        Args:
            user_id: User ID
            place_id: Place ID
            
        Returns:
            Optional[UserPlaceFavorites]: The created favorite record or None if failed
        """
        item_data = {
            "user_id": user_id,
            "place_id": place_id
        }
        return self.core.add(item_data)
    
    def get_user_favorites(self, user_id: str) -> List[UserPlaceFavorites]:
        """
        Get all places a user has favorited
        
        Args:
            user_id: User ID
            
        Returns:
            List[UserPlaceFavorites]: List of favorite records
        """
        return self.core.get_by_filter(user_id=user_id)
    
    def get_user_favorite_counts(self, user_id: str) -> List[UserPlaceFavoriteCount]:
        """
        Get count of how many times a user favorited each place
        
        Args:
            user_id: User ID
            
        Returns:
            List[UserPlaceFavoriteCount]: List of place IDs with favorite counts and last favorited time
        """
        results = (
            self.db.query(
                UserPlaceFavorites.place_id,
                func.count(UserPlaceFavorites.id).label("favorite_count"),
                func.max(UserPlaceFavorites.created_at).label("last_favorited_at")
            )
            .filter(UserPlaceFavorites.user_id == user_id)
            .group_by(UserPlaceFavorites.place_id)
            .all()
        )
        
        return [
            UserPlaceFavoriteCount(
                place_id=result.place_id,
                favorite_count=result.favorite_count,
                last_favorited_at=result.last_favorited_at
            )
            for result in results
        ]
    
    def get_most_recently_favorited(self, user_id: str, limit: int = 10) -> List[UserPlaceFavorites]:
        """
        Get most recently favorited places by a user
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List[UserPlaceFavorites]: List of favorite records sorted by most recent
        """
        return (
            self.db.query(UserPlaceFavorites)
            .filter(UserPlaceFavorites.user_id == user_id)
            .order_by(desc(UserPlaceFavorites.created_at))
            .limit(limit)
            .all()
        )
    
    def remove_favorite(self, favorite_id: int) -> bool:
        """
        Remove a specific favorite by ID
        
        Args:
            favorite_id: ID of the favorite record
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            favorite = self.db.query(UserPlaceFavorites).filter(UserPlaceFavorites.id == favorite_id).first()
            if not favorite:
                return False
                
            self.db.delete(favorite)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error removing favorite: {str(e)}")
            return False
            
# Create a singleton instance with a default database session
user_place_favorites_service = UserPlaceFavoritesService(next(get_db()))