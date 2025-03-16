from models.PlacePost import Base, engine, get_db
from models.Place import Place
from models.Post import Post
from models.User import User
from models.UserNote import UserNote
from models.UserFavorites import UserFavorites
from models.UserPlaceFavorites import UserPlaceFavorites

def init_db():
    """
    Initialize the database schema.
    This will create all tables and relationships.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

def drop_db():
    """
    Drop all tables in the database.
    WARNING: This will delete all data!
    """
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped successfully.")

def reset_db():
    """
    Reset the database by dropping and recreating all tables.
    WARNING: This will delete all data!
    """
    drop_db()
    init_db()
    print("Database reset completed successfully.")

def migrate_data():
    """
    This function can be used to migrate data from external sources.
    For example, from Elasticsearch to MySQL or between tables.
    """
    # Get a database session
    db = next(get_db())
    
    try:
        # Add your migration logic here
        print("Starting data migration...")
        
        # Example: Check if tables are empty
        place_count = db.query(Place).count()
        post_count = db.query(Post).count()
        user_count = db.query(User).count()
        
        print(f"Current record counts - Places: {place_count}, Posts: {post_count}, Users: {user_count}")
        
        # Example migration code would go here
        # ...
        
        db.commit()
        print("Data migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {str(e)}")
    finally:
        db.close()
        
def clear_user_notes():
    """
    Clear all records from the user_notes table without dropping the table structure.
    """
    # Get a database session
    db = next(get_db())
    
    try:
        # Delete all records from user_notes table
        deleted_count = db.query(UserNote).delete()
        db.commit()
        print(f"Successfully deleted {deleted_count} records from user_notes table.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing user_notes table: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_migration.py [init|drop|reset|migrate|clear_user_notes]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_db()
    elif command == "drop":
        confirm = input("WARNING: This will delete all data! Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            drop_db()
        else:
            print("Operation cancelled.")
    elif command == "reset":
        confirm = input("WARNING: This will delete all data! Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            reset_db()
        else:
            print("Operation cancelled.")
    elif command == "migrate":
        migrate_data()
    elif command == "clear_user_notes":
        confirm = input("This will delete all records from the user_notes table. Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            clear_user_notes()
        else:
            print("Operation cancelled.")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, drop, reset, migrate, clear_user_notes")
        sys.exit(1)