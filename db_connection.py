import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Connection pool configuration
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    database=os.getenv("PGDATABASE")
)

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles connection acquisition and release.
    """
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database cursors.
    Automatically handles transaction commit/rollback.
    
    Args:
        commit (bool): Whether to commit the transaction after execution
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

def test_connection():
    """Test the database connection"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
            print("Database connection successful! Current time:", result[0])
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()