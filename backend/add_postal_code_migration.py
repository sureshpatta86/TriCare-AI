"""
Migration script to add postal_code column to users table
Run this script from the backend directory:
    python add_postal_code_migration.py
"""

import sqlite3
import os

def migrate():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'tricare.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("The database will be created when the backend starts.")
        print("No migration needed - postal_code column will be included automatically.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if postal_code column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'postal_code' in columns:
            print("✓ postal_code column already exists in users table")
        else:
            # Add the postal_code column
            print("Adding postal_code column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN postal_code VARCHAR")
            conn.commit()
            print("✓ Successfully added postal_code column to users table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\nCurrent users table columns: {', '.join(columns)}")
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("TriCare Database Migration: Add postal_code to users table")
    print("=" * 60)
    migrate()
    print("=" * 60)
