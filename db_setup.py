from db_connection import get_db_cursor
import time

def init_db(recreate_tables=False):
    """Initialize the database and create all tables"""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Test connection
            cursor.execute("SELECT NOW();")
            print("Successfully connected to database")

            if recreate_tables:
                # Drop existing tables if they exist
                print("Dropping existing tables...")
                drop_tables_sql = """
                    DROP TABLE IF EXISTS public.urls CASCADE;
                    DROP TABLE IF EXISTS public.users CASCADE;
                    DROP TABLE IF EXISTS public.global_counter CASCADE;
                """
                cursor.execute(drop_tables_sql)
                # Wait a moment for tables to be fully dropped
                time.sleep(1)
            
            # Create tables one by one
            print("Creating users table...")
            create_users_sql = """
                CREATE TABLE IF NOT EXISTS public.users (
                    user_id SERIAL PRIMARY KEY
                );
            """
            cursor.execute(create_users_sql)
            
            print("Creating urls table...")
            create_urls_sql = """
                CREATE TABLE IF NOT EXISTS public.urls (
                    id SERIAL PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    shortened_url TEXT UNIQUE NOT NULL,
                    custom_domain TEXT,
                    expires_at TIMESTAMP,
                    custom_alias TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES public.users(user_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_shortened_url ON public.urls(shortened_url);
                CREATE INDEX IF NOT EXISTS idx_original_url ON public.urls(original_url);
                CREATE INDEX IF NOT EXISTS idx_custom_alias ON public.urls(custom_alias);
            """
            cursor.execute(create_urls_sql)
            
            print("Creating global counter table...")
            create_counter_sql = """
                CREATE TABLE IF NOT EXISTS public.global_counter (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    current_value BIGINT DEFAULT 1000000,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT single_row CHECK (id = 1)
                );
                
                INSERT INTO public.global_counter (id, current_value)
                VALUES (1, 1000000)
                ON CONFLICT (id) DO NOTHING;
            """
            cursor.execute(create_counter_sql)
            
            # Enable RLS
            print("Enabling Row Level Security...")
            enable_rls_sql = """
                ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
                ALTER TABLE public.urls ENABLE ROW LEVEL SECURITY;
                ALTER TABLE public.global_counter ENABLE ROW LEVEL SECURITY;
                
                DROP POLICY IF EXISTS "Enable read access for all users" ON public.urls;
                CREATE POLICY "Enable read access for all users" ON public.urls
                    FOR SELECT USING (true);
                
                DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.urls;
                CREATE POLICY "Enable insert for authenticated users only" ON public.urls
                    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
            """
            cursor.execute(enable_rls_sql)
            
            # Add default user if none exists
            print("Checking for default user...")
            cursor.execute("SELECT * FROM public.users LIMIT 1")
            if not cursor.fetchone():
                print("Creating default user...")
                cursor.execute("INSERT INTO public.users (user_id) VALUES (1)")
            
            print("Database setup complete!")
            
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    # Ask user if they want to reset the existing tables
    response = input("Do you want to reset the existing tables? (yes/no): ").lower()
    recreate_tables = response in ['yes', 'y']
    
    init_db(recreate_tables)