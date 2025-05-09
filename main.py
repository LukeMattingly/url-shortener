from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="URL Shortener API")

@app.get("/")
async def root():
    return {"message": "Welcome to the URL Shortener API"}

@app.get("/shortenUrl")
async def shorten_url(url: str):
    """
    Shorten a URL with an optional custom alias and expiration date and custom domain.
    """

    
    if not url:
        return {"error": "URL is required"}
  
    # use a global counter to generate a unique ID for the shortened URL
    #redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    #new_value = redis_client.incr("global_url_counter")

    Counter = 1
    shortened_url = f"http://short.ly/{Counter}"
    Counter += 1


    return {
        "original_url": url,
        "shortened_url": shortened_url, 
    }

@app.get("/customShortenUrl")
async def custom_shorten_url(url: str, custom_alias: str, expires_at: str = None, custom_domain: str = None):

      
    if not url:
        return {"error": "URL is required"}

      
    if expires_at:
        # Validate the expiration date format (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(expires_at, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid expiration date format. Use YYYY-MM-DD."}
        
        # verify expiration date is in the future
        if datetime.strptime(expires_at, "%Y-%m-%d") < datetime.now():
            return {"error": "Expiration date must be in the future."}
        
    baseDomain = "http://short.ly"
    if custom_domain:
        #TODO check against my sqlite db if the custom domain already exists and if this user has access to it
        baseDomain = custom_domain

    shortened_url = f"{baseDomain}/{custom_alias}" if custom_alias else f"{baseDomain}/{url.split('/')[-1]}"


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



