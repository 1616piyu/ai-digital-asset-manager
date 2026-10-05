import sqlite3

DB_PATH = "storage/database.db"

conn = sqlite3.connect(DB_PATH)

query = """
SELECT filename, ai_description
FROM assets
WHERE file_type = 'image'
AND (
    filename LIKE '%bulat%'
    OR filename LIKE '%tima%'
)
"""

rows = conn.execute(query).fetchall()

for filename, description in rows:
    print()
    print("=" * 70)
    print("FILE:", filename)
    print("DESCRIPTION:")
    print(description)

conn.close()