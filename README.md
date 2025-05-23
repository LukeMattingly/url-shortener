# Basic URL Shortener

## simple public endpoint for shortening urls

## private endpoint for custom domains, expiry times, custom aliases, analytics, exporting etc

## To Setup 

```py 
python -m venv venv
```

## To run
```
uvicorn main:app --reload
```

## Test out shortening a url

`curl -X POST http://localhost:8000/shortenUrl -H "Content-Type: application/json" -d "{\"url\": \"https://example.com\"}"`

`curl -X POST http://localhost:8000/customShortenUrl -H "Content-Type: application/json" -d "{\"url\": \"https://walmart.com/123\", \"custom_alias\": \"luke324\", \"expires_at\": \"2026-12-12\", \"custom_domain\": \"shorten.me\", \"user_id\": 111}"`


## Database Setup

The project uses SQLite as its database. To set up or reset the database:

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the database setup script:
   ```
   python db_setup.py
   ```

The script will ask if you want to reset the existing database. Type 'yes' or 'y' to reset it, or 'no' or 'n' to keep existing data.

This will:
- Create the database if it doesn't exist
- Set up all required tables
- Create a default user (ID: 1)

If you need to completely reset the database, run the setup script and choose 'yes' when prompted to reset.

# TODO 
[X] - add in the base redirect functionality for when someone calls with a shortened url and you redir them to the correct long url location

[X] - change from GET to POST for creating new shortened urls

[ ] do base 62 encoding for url so that it's real, and not just a counter

[ ] move the database to supabase so that I can deploy it
(keep secrets secret)

[ ] add a UI - sveltkit, simple single page. where you can shorten urls

[ ] setup fly, deploy UI and backend


---------
Nice to haves

- add in expires logic

- allow users to add custom domains (make sure there's no conflict where someone else already owns it)
- add validation if a custom domain is sent in to make sure that domain belong to that url

- add in analytics for how often requests are being made for a certain url. (request count + time of each request so you can track it over time)