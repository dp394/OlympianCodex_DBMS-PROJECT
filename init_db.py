"""
Initialize the SQLite database for The Olympian Codex.
Run this script once to create and populate the database.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'olympian_codex.db')

def init_database():
    """Create and populate the SQLite database."""
    # Remove existing database if present
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print("Schema created successfully!")

    # Read and execute populate
    populate_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'populate.sql')
    with open(populate_path, 'r', encoding='utf-8') as f:
        populate_sql = f.read()
    conn.executescript(populate_sql)
    print("Data populated successfully!")

    # Verify
    cursor = conn.cursor()
    tables = ['God', 'Demigod', 'Monster', 'Prophecy', 'Quest', 'Divine_Artifact',
              'Quest_Log', 'Sighting_Log', 'Known_Abilities', 'Combat_Encounter', 'Rescue_Mission']
    print("\n--- Summary Statistics ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")

    conn.close()
    print(f"\nDatabase created at: {DB_PATH}")

if __name__ == '__main__':
    init_database()
