import sqlite3
import os
import sys

from const import DATABASE_PATH

def validate_database(db_path):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Fetch all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                print("No tables found in the database.")
                return
            
            for table_name, in tables:
                print(f"\nValidating table: {table_name}")
                
                # Fetch table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                schema = cursor.fetchall()
                
                if not schema:
                    print(f"  Warning: Table '{table_name}' has no schema.")
                    continue
                
                column_definitions = {col[1]: col for col in schema}  # {column_name: schema_row}
                
                # Fetch all rows from the table
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                
                if not rows:
                    print(f"  Info: Table '{table_name}' has no rows.")
                    continue
                
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        col_name = schema[col_idx][1]
                        col_type = schema[col_idx][2]
                        not_null = schema[col_idx][3]
                        
                        # Validate NOT NULL constraint
                        if not_null and value is None:
                            print(f"    Error in row {row_idx + 1}: Column '{col_name}' is NULL but must not be.")
                            continue
                        
                        # Validate column type
                        if value is not None:
                            if not validate_type(value, col_type):
                                print(f"    Error in row {row_idx + 1}: Column '{col_name}' has invalid type '{type(value).__name__}', expected '{col_type}'.")
            
            print("\nValidation completed.")
    
    except sqlite3.Error as e:
        print(f"Error while validating database: {e}")

def validate_type(value, expected_type):
    """
    Validate if a value matches the expected SQLite type.
    """
    if expected_type.upper() in ("TEXT", "CHAR", "VARCHAR"):
        return isinstance(value, str)
    elif expected_type.upper() in ("INTEGER", "INT"):
        return isinstance(value, int)
    elif expected_type.upper() in ("REAL", "FLOAT", "DOUBLE"):
        return isinstance(value, (float, int))
    elif expected_type.upper() == "BLOB":
        return isinstance(value, (bytes, memoryview))
    return True  # SQLite is lenient with type checking, so assume true if uncertain

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_db.py <database_file>")
    else:
        db_path = sys.argv[1]
        validate_database(db_path)
