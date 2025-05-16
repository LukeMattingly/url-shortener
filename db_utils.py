import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def add_column(table_name: str, column_name: str, column_type: str):
    """
    Add a new column to an existing table in Supabase.
    
    Args:
        table_name (str): Name of the table to modify
        column_name (str): Name of the new column
        column_type (str): PostgreSQL type of the new column (e.g., 'TEXT', 'INTEGER', 'TIMESTAMP')
    """
    try:
        # Check if column exists using Postgres information schema
        query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND column_name = '{column_name}'
        """
        
        result = supabase.table(table_name).select("*").execute()
        columns = result.data[0].keys() if result.data else []
        
        if column_name in columns:
            print(f"Column '{column_name}' already exists in table '{table_name}'")
            return False
        
        # Add the new column using PostgreSQL ALTER TABLE
        alter_query = f"""
        ALTER TABLE {table_name} 
        ADD COLUMN {column_name} {column_type}
        """
        
        supabase.rpc('exec', {'query': alter_query})
        print(f"Successfully added column '{column_name}' to table '{table_name}'")
        return True
        
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    table_name = input("Enter table name: ")
    column_name = input("Enter new column name: ")
    column_type = input("Enter column type (TEXT, INTEGER, TIMESTAMP, etc.): ")
    
    add_column(table_name, column_name, column_type.upper())