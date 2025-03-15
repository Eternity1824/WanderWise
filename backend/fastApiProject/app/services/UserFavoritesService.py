from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.UserFavorites import UserFavorites
from models.PlacePost import get_db
from core.MySqlCore import MySqlCore
from services.PostService import post_service
from services.UserNoteService import user_note_service

class UserFavoritesService:
    """Handles operations for user favorites"""

    def __init__(self, db: Session = next(get_db())):
        """
        Initialize UserFavoritesService
        
        Args:
            db: Database session, default from get_db
        """
        self.mysql_core = MySqlCore(db, UserFavorites)
    
    def add_favorite(self, user_id: str, post_id: str) -> Optional[UserFavorites]:
        """
        Add a post to user's favorites
        
        Args:
            user_id: User ID
            post_id: Post ID
            
        Returns:
            Optional[UserFavorites]: Created record, None if failed
        """
        # First check if post exists
        post = post_service.get_post_by_id(post_id)
        if not post:
            return None
            
        # Check if already favorited
        existing = self.mysql_core.get_by_filter(user_id=user_id, post_id=post_id)
        if existing:
            return existing[0]  # Already favorited, just return the existing record
            
        # Create favorite record
        item_data = {
            "user_id": user_id,
            "post_id": post_id
        }
        
        try:
            # Add favorite record
            favorite = self.mysql_core.add(item_data)
            
            # Increment the user's favorite count
            if favorite:
                user_note_service.increment_favorite_count(user_id)
                
            return favorite
            
        except IntegrityError:
            self.mysql_core.db.rollback()
            # Already favorited, just return the existing record
            existing = self.mysql_core.get_by_filter(user_id=user_id, post_id=post_id)
            if existing:
                return existing[0]
            return None
    
    def remove_favorite(self, user_id: str, post_id: str) -> bool:
        """
        Remove a post from user's favorites
        
        Args:
            user_id: User ID
            post_id: Post ID
            
        Returns:
            bool: True if successfully removed, False otherwise
        """
        try:
            records = self.mysql_core.get_by_filter(user_id=user_id, post_id=post_id)
            if not records:
                return False
                
            self.mysql_core.db.query(UserFavorites).filter(
                UserFavorites.user_id == user_id, 
                UserFavorites.post_id == post_id
            ).delete()
            self.mysql_core.db.commit()
            
            # Decrement the user's favorite count
            user_note_service.decrement_favorite_count(user_id)
            
            return True
        except Exception as e:
            self.mysql_core.db.rollback()
            print(f"Failed to remove favorite: {str(e)}")
            return False
    
    def get_user_favorites(self, user_id: str) -> List[UserFavorites]:
        """
        Get all favorite posts for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[UserFavorites]: List of user favorite records
        """
        return self.mysql_core.get_by_filter(user_id=user_id)
    
    def get_user_favorite_posts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all favorite post details for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[Dict[str, Any]]: List of post details
        """
        favorites = self.get_user_favorites(user_id)
        posts = []
        
        for favorite in favorites:
            post = post_service.get_post_by_id(favorite.post_id)
            if post:
                posts.append(post)
                
        return posts
    
    def get_favorite_count(self, user_id: str) -> int:
        """
        Get the number of posts favorited by a user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Count of favorited posts
        """
        # Use the UserNote service to get the count
        return user_note_service.get_favorite_count(user_id)
    
    def is_post_favorited(self, user_id: str, post_id: str) -> bool:
        """
        Check if a post is favorited by a user
        
        Args:
            user_id: User ID
            post_id: Post ID
            
        Returns:
            bool: True if post is favorited, False otherwise
        """
        records = self.mysql_core.get_by_filter(user_id=user_id, post_id=post_id)
        return len(records) > 0
    
    def sync_favorite_count(self, user_id: str) -> int:
        """
        Synchronize the user's favorite count with the actual number of favorites
        
        Args:
            user_id: User ID
            
        Returns:
            int: Updated favorite count
        """
        # Get actual count of favorites
        favorites = self.get_user_favorites(user_id)
        actual_count = len(favorites)
        
        # Get existing records from UserNote
        existing_records = user_note_service.mysql_core.get_by_filter(user_id=user_id)
        
        if existing_records:
            # Update the count to match actual favorites
            existing_record = existing_records[0]
            existing_record.post_count = actual_count
            user_note_service.mysql_core.db.commit()
            return actual_count
        elif actual_count > 0:
            # Create new record with correct count
            item_data = {
                "user_id": user_id,
                "post_count": actual_count
            }
            record = user_note_service.mysql_core.add(item_data)
            return record.post_count if record else 0
        
        return 0

# Create singleton instance
user_favorites_service = UserFavoritesService()