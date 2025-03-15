from fastapi.testclient import TestClient
from main import app
from models.PlacePost import Base, engine
from models.UserPlaceFavorites import UserPlaceFavorites
from sqlalchemy.orm import sessionmaker
import uuid

client = TestClient(app)

def setup():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Clean up test data
    db.query(UserPlaceFavorites).filter(
        UserPlaceFavorites.user_id == "test_api_user"
    ).delete()
    db.commit()
    db.close()

def teardown():
    # Create a test session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Clean up test data
    db.query(UserPlaceFavorites).filter(
        UserPlaceFavorites.user_id == "test_api_user"
    ).delete()
    db.commit()
    db.close()

def test_user_place_favorites_api():
    try:
        setup()
        
        user_id = "test_api_user"
        place_ids = [f"place_{uuid.uuid4().hex[:8]}" for _ in range(3)]
        
        # Test adding favorites
        for place_id in place_ids:
            # Add each place twice
            for _ in range(2):
                response = client.post(f"/user/{user_id}/place/{place_id}/favorite")
                assert response.status_code == 200
                data = response.json()
                assert data["user_id"] == user_id
                assert data["place_id"] == place_id
                assert "created_at" in data
        
        # Test getting all favorites
        response = client.get(f"/user/{user_id}/favorites")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6  # 3 places * 2 times each
        
        # Test getting favorite counts
        response = client.get(f"/user/{user_id}/favorites/counts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 3 unique places
        for item in data:
            assert item["favorite_count"] == 2  # Each place favorited 2 times
        
        # Test getting recent favorites
        response = client.get(f"/user/{user_id}/favorites/recent?limit=4")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Limited to 4
        
        # Test removing a favorite
        favorite_id = data[0]["id"]  # Get the ID of the first favorite
        response = client.delete(f"/user/favorites/{favorite_id}")
        assert response.status_code == 200
        
        # Verify it was removed
        response = client.get(f"/user/{user_id}/favorites")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # One removed from 6
        
        print("All API tests passed!")
        
    finally:
        teardown()

if __name__ == "__main__":
    test_user_place_favorites_api()