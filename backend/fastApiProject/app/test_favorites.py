# test_favorites.py
from services import user_favorites_service, user_place_favorites_service

def test_user_favorites():
    # Test user post favorites
    print("Getting favorite posts for user123...")
    favorite_posts = user_favorites_service.get_user_favorite_posts(user_id="user123")
    print(f"Found {len(favorite_posts)} favorite posts:")
    for post in favorite_posts:
        print(f"  - {post['title']} (ID: {post['note_id']})")
    
    # Test if post is favorited
    print("\nChecking if user456 favorited post 6554db7e0000000032029d16...")
    is_favorited = user_favorites_service.is_post_favorited(
        user_id="user456", 
        post_id="6554db7e0000000032029d16"
    )
    print(f"Is favorited: {is_favorited}")
    
    # Test user place favorites
    print("\nGetting place favorites for user789...")
    place_favorites = user_place_favorites_service.get_user_favorites(user_id="user789")
    print(f"Found {len(place_favorites)} place favorites:")
    for fav in place_favorites:
        print(f"  - Place: {fav.place.name} (ID: {fav.place_id}), favorited at {fav.created_at}")
    
    # Test getting recent place favorites
    print("\nGetting recent place favorites for user123...")
    recent_favorites = user_place_favorites_service.get_most_recently_favorited(
        user_id="user123",
        limit=2
    )
    print(f"Found {len(recent_favorites)} recent favorites:")
    for fav in recent_favorites:
        print(f"  - Place: {fav.place.name} (ID: {fav.place_id}), favorited at {fav.created_at}")

if __name__ == "__main__":
    test_user_favorites()