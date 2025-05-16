from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import string
from db_connection import get_db_cursor

class URLCreateRequest(BaseModel):
    url: str

class CustomURLCreateRequest(BaseModel):
    url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[str] = None
    custom_domain: Optional[str] = None
    user_id: Optional[int] = None

# Base62 character set (0-9, a-z, A-Z)
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode_base62(num):
    """Encode a number to base62 string"""
    if num == 0:
        return ALPHABET[0]
    
    arr = []
    base = len(ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

def decode_base62(string):
    """Decode a base62 string to number"""
    num = 0
    base = len(ALPHABET)
    for char in string:
        num = num * base + ALPHABET.index(char)
    return num

def get_next_counter():
    """Get next counter value using row-level locking transaction"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            UPDATE global_counter 
            SET current_value = current_value + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
            RETURNING current_value;
        """)
        result = cursor.fetchone()
        return result[0]

app = FastAPI(title="URL Shortener API")

@app.get("/{alias}")
async def redirect_url(alias: str):
    """Redirect to the original URL using the shortened URL alias."""
    if not alias:
        return {"error": "Alias is required"}
    
    with get_db_cursor() as cursor:
        # Try to find URL by custom alias first
        cursor.execute("""
            SELECT original_url FROM urls 
            WHERE custom_alias = %s 
            OR shortened_url = %s
        """, (alias, f"http://short.ly/{alias}"))
        
        result = cursor.fetchone()
        
        if result:
            return RedirectResponse(url=result[0], status_code=307)
        else:
            raise HTTPException(status_code=404, detail="URL not found")

@app.post("/shortenUrl")
async def shorten_url(url_request: URLCreateRequest):
    """Shorten a URL with an automatically generated base62 alias."""
    if not url_request.url:
        return {"error": "URL is required"}
    
    # Get next counter value in transaction
    counter = get_next_counter()
    
    # Generate base62 encoded counter
    encoded_id = encode_base62(counter)
    shortened_url = f"http://short.ly/{encoded_id}"
    
    # Create new URL entry
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            INSERT INTO urls (original_url, shortened_url, created_at)
            VALUES (%s, %s, %s)
            RETURNING original_url, shortened_url
        """, (url_request.url, shortened_url, datetime.utcnow()))
        
        result = cursor.fetchone()
        
        return {
            "original_url": result[0],
            "shortened_url": result[1],
        }

@app.post("/customShortenUrl")
async def custom_shorten_url(url_request: CustomURLCreateRequest):
    """Shorten a URL with custom parameters."""
    if url_request.user_id is None:
        return {"error": "User ID is required"}
    
    if not url_request.url:
        return {"error": "URL is required"}

    if url_request.expires_at:
        try:
            expires_at = datetime.strptime(url_request.expires_at, "%Y-%m-%d")
            if expires_at < datetime.now():
                return {"error": "Expiration date must be in the future."}
        except ValueError:
            return {"error": "Invalid expiration date format. Use YYYY-MM-DD."}
    
    base_domain = "http://short.ly"
    if url_request.custom_domain:
        base_domain = url_request.custom_domain

    shortened_url = f"{base_domain}/{url_request.custom_alias}" if url_request.custom_alias else f"{base_domain}/{url_request.url.split('/')[-1]}"

    # Check if shortened URL already exists
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM urls WHERE shortened_url = %s", (shortened_url,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="This shortened URL already exists")

    # Create new URL entry
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            INSERT INTO urls (
                original_url, shortened_url, custom_domain, 
                custom_alias, expires_at, created_at, created_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            url_request.url, shortened_url, url_request.custom_domain,
            url_request.custom_alias, url_request.expires_at,
            datetime.utcnow(), url_request.user_id
        ))
        
        created_url = cursor.fetchone()
        
        return {
            "original_url": url_request.url,
            "created_by": url_request.user_id,
            "created_at": created_url[6],  # Index of created_at in the returned tuple
            "expires_at": created_url[4],  # Index of expires_at
            "custom_alias": url_request.custom_alias,
            "custom_domain": url_request.custom_domain,
            "shortened_url": shortened_url,
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



