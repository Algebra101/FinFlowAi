"""Migrate the old database schema to add columns required by the new models."""
import sqlite3

conn = sqlite3.connect("fincore.db")
cursor = conn.cursor()

migrations = [
    ("fraud_flags", "details", "ALTER TABLE fraud_flags ADD COLUMN details TEXT"),
    ("transactions", "source", "ALTER TABLE transactions ADD COLUMN source TEXT DEFAULT 'squad'"),
    ("sme_users", "created_at", "ALTER TABLE sme_users ADD COLUMN created_at DATETIME"),
]

for table, col, sql in migrations:
    try:
        cursor.execute(sql)
        print(f"  Added: {table}.{col}")
    except Exception as e:
        print(f"  Skipped: {table}.{col} ({e})")

conn.commit()
conn.close()
print("\nDatabase schema migration complete!")
