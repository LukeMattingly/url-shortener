from sqlalchemy import create_engine, text
from main import SQLALCHEMY_DATABASE_URL

def add_column(table_name: str, column_name: str, column_type: str):
    """
    Add a new column to an existing table.
    
    Args:
        table_name (str): Name of the table to modify
        column_name (str): Name of the new column
        column_type (str): SQL type of the new column (e.g., 'TEXT', 'INTEGER', 'DATETIME')
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Check if column already exists
    with engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result]
        
        if column_name in columns:
            print(f"Column '{column_name}' already exists in table '{table_name}'")
            return False
        
        # Add the new column
        try:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            print(f"Successfully added column '{column_name}' to table '{table_name}'")
            return True
        except Exception as e:
            print(f"Error adding column: {str(e)}")
            return False

if __name__ == "__main__":
    # Example usage
    table_name = input("Enter table name: ")
    column_name = input("Enter new column name: ")
    column_type = input("Enter column type (TEXT, INTEGER, DATETIME, etc.): ")
    
    add_column(table_name, column_name, column_type.upper())