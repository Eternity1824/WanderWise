from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.UserNote import UserNote
from models.PlacePost import get_db
from core.MySqlCore import MySqlCore

class UserNoteService:
    """Handles operations for user notes tracking"""

    def __init__(self, db: Session = next(get_db())):
        """
        Initialize UserNoteService
        
        Args:
            db: Database session, default from get_db
        """
        self.mysql_core = MySqlCore(db, UserNote)
    
    def clear_database(self) -> bool:
        """
        Clear all data in user_notes table
        
        Returns:
            bool: True if operation successful
        """
        return self.mysql_core.clear_table()
    
    def add_or_update_user_note_count(self, user_id: str, count: int = 1) -> Optional[UserNote]:
        """
        Add a new user note record or update the count if it exists
        
        Args:
            user_id: User ID
            count: Number to increment the post_count by, default 1
            
        Returns:
            Optional[UserNote]: Updated record, None if failed
        """
        # Check if user already exists
        existing_records = self.mysql_core.get_by_filter(user_id=user_id)
        
        if existing_records:
            # User exists, update count
            existing_record = existing_records[0]
            existing_record.post_count += count
            self.mysql_core.db.commit()
            return existing_record
        else:
            # User doesn't exist, create new record
            item_data = {
                "user_id": user_id,
                "post_count": count
            }
            return self.mysql_core.add(item_data)
    
    def get_user_note_count(self, user_id: str) -> int:
        """
        Get the post count for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Post count for the user, 0 if user not found
        """
        records = self.mysql_core.get_by_filter(user_id=user_id)
        if records:
            return records[0].post_count
        return 0
    
    def get_all_user_notes(self) -> List[UserNote]:
        """
        Get all user note records
        
        Returns:
            List[UserNote]: List of all user note records
        """
        return self.mysql_core.get_all()

# Create singleton instance
user_note_service = UserNoteService()