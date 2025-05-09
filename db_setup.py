import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, User, URL

def init_db(drop_existing=False):
    """Initialize the database and create all tables."""
    # Database URL from main application
    SQLALCHEMY_DATABASE_URL = "sqlite:///./urls.db"
    
    # If drop_existing is True and the database file exists, remove it
    if drop_existing and os.path.exists("urls.db"):
        try:
            os.remove("urls.db")
            print("Existing database removed.")
        except PermissionError:
            print("Could not remove existing database. Make sure it's not in use.")
            return
    
    # Create database engine
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create a session to add initial data if needed
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Add a default user if none exists
        if not db.query(User).first():
            default_user = User(user_id=1)
            db.add(default_user)
            db.commit()
            print("Created default user with ID 1")
        
        db.close()
    except Exception as e:
        print(f"Error adding initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ask user if they want to drop existing database
    response = input("Do you want to reset the existing database? (yes/no): ").lower()
    drop_existing = response in ['yes', 'y']
    
    init_db(drop_existing)
    print("Database setup complete!")