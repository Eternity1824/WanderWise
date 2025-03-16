from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.PlacePost import Base
from models.UserPlaceFavorites import UserPlaceFavorites
from services.UserPlaceFavoritesService import UserPlaceFavoritesService, user_place_favorites_service
from config import get_settings
import datetime
import time

def test_user_place_favorites():
    """Test user place favorites functionality"""
    
    settings = get_settings()
    
    # Create a test database engine
    engine = create_engine(settings.MYSQL_CONNECTION_STRING)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a Session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Clean up any existing test data
        db.query(UserPlaceFavorites).filter(
            UserPlaceFavorites.user_id == "test_user"
        ).delete()
        db.commit()
        
        # Create service
        service = UserPlaceFavoritesService(db)
        
        # Test adding favorites
        place_ids = ["place1", "place2", "place3"]
        
        # Add each place multiple times
        for place_id in place_ids:
            for _ in range(3):  # Add each place 3 times
                favorite = service.add_favorite("test_user", place_id)
                assert favorite is not None
                assert favorite.user_id == "test_user"
                assert favorite.place_id == place_id
                time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Test getting user favorites
        favorites = service.get_user_favorites("test_user")
        assert len(favorites) == 9  # 3 places * 3 times each
        
        # Test getting favorite counts
        counts = service.get_user_favorite_counts("test_user")
        assert len(counts) == 3  # 3 unique places
        
        for count in counts:
            assert count.favorite_count == 3  # Each place favorited 3 times
            assert isinstance(count.last_favorited_at, datetime.datetime)
        
        # Test getting recent favorites
        recent = service.get_most_recently_favorited("test_user", 5)
        assert len(recent) == 5  # Limited to 5
        
        # Verify the recent favorites are in correct order (most recent first)
        for i in range(len(recent) - 1):
            assert recent[i].created_at >= recent[i + 1].created_at
        
        # Test removing a favorite
        first_favorite_id = favorites[0].id
        result = service.remove_favorite(first_favorite_id)
        assert result is True
        
        # Verify it was removed
        updated_favorites = service.get_user_favorites("test_user")
        assert len(updated_favorites) == 8  # One removed from 9
        
        print("All tests passed!")
        
    finally:
        # Clean up
        db.query(UserPlaceFavorites).filter(
            UserPlaceFavorites.user_id == "test_user"
        ).delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    test_user_place_favorites()