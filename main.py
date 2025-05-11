from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./urls.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    shortened_url = Column(String, unique=True, index=True)
    custom_domain = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    custom_alias = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.user_id"))

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="URL Shortener API")

@app.get("/{alias}")
async def redirectUrl(alias: str, db: Session = Depends(get_db)):
    """
    Redirect to the original URL using the shortened URL alias.
    """
    print(f"alias: {alias}\n")  
    if not alias:
        return {"error": "Alias is required"}
    
    db_url = db.query(URL).filter(URL.custom_alias == alias).first()
    if db_url:
        return RedirectResponse(url=db_url.original_url, status_code=307)
    else:
        raise HTTPException(status_code=404, detail="URL not found")


@app.get("/shortenUrl")
async def shorten_url(
    # URL query parameters
    url: str,
    # Dependencies
    *,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Shorten a URL with an optional custom alias and expiration date and custom domain.
    """
    
    if not url:
        return {"error": "URL is required"}
    
    Counter = db.query(URL).count() + 1
    shortened_url = f"http://short.ly/{Counter}"

    # Create new URL entry
    db_url = URL(
        original_url=url,
        shortened_url=shortened_url,
        created_by=user_id,
        expires_at=None,
        custom_alias=None,
        custom_domain=None
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return {
        "original_url": url,
        "shortened_url": shortened_url,
    }

@app.get("/customShortenUrl")
async def custom_shorten_url(
    # URL query parameters
    url: str, 
    custom_alias: str, 
    expires_at: str = None, 
    custom_domain: str = None,
    # Dependencies
    *,
    db: Session = Depends(get_db),
    user_id: int = None
):
    if user_id is None:
        return {"error": "User ID is required"}
    
    if not url:
        return {"error": "URL is required"}

    if expires_at:
        try:
            datetime.strptime(expires_at, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid expiration date format. Use YYYY-MM-DD."}
        
        if datetime.strptime(expires_at, "%Y-%m-%d") < datetime.now():
            return {"error": "Expiration date must be in the future."}
        
    base_domain = "http://short.ly"
    if custom_domain:
        base_domain = custom_domain

    shortened_url = f"{base_domain}/{custom_alias}" if custom_alias else f"{base_domain}/{url.split('/')[-1]}"

    # Check if shortened URL already exists
    existing_url = db.query(URL).filter(URL.shortened_url == shortened_url).first()
    if existing_url:
        raise HTTPException(status_code=400, detail="This shortened URL already exists")

    # Create new URL entry
    db_url = URL(
        original_url=url,
        shortened_url=shortened_url,
        custom_domain=custom_domain,
        expires_at=datetime.strptime(expires_at, "%Y-%m-%d") if expires_at else None,
        custom_alias=custom_alias,
        created_at=datetime.utcnow(),
        created_by=user_id, 
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return {
        "original_url": url,
        "custom_alias": custom_alias,
        "expires_at": expires_at,
        "custom_domain": custom_domain,
        "shortened_url": shortened_url,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



