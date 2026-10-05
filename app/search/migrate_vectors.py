import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import (
    initialize_database,
    get_connection
)


def migrate_existing_vectors():

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # Find assets that already have FAISS vector IDs
    cursor.execute(
        """
        SELECT
            id,
            filename,
            vector_id,
            ai_description
        FROM assets
        WHERE vector_id IS NOT NULL
        ORDER BY vector_id
        """
    )

    assets = cursor.fetchall()

    if not assets:

        print("No existing vectors found.")
        connection.close()
        return

    print()
    print("=" * 60)
    print("VECTOR MIGRATION")
    print("=" * 60)
    print()

    migrated = 0
    skipped = 0

    for asset in assets:

        # Check whether this vector is already registered
        cursor.execute(
            """
            SELECT id
            FROM asset_vectors
            WHERE vector_id = ?
            """,
            (asset["vector_id"],)
        )

        existing = cursor.fetchone()

        if existing:

            print(
                f"[SKIPPED] "
                f"{asset['filename']} "
                f"(Vector {asset['vector_id']} already exists)"
            )

            skipped += 1
            continue

        cursor.execute(
            """
            INSERT INTO asset_vectors (
                asset_id,
                vector_id,
                content_type,
                content_text,
                timestamp_seconds
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                asset["id"],
                asset["vector_id"],
                "asset",
                asset["ai_description"],
                None
            )
        )

        print(
            f"[MIGRATED] "
            f"{asset['filename']} "
            f"→ Vector {asset['vector_id']}"
        )

        migrated += 1

    connection.commit()

    # Display final mapping
    print()
    print("-" * 60)
    print("VECTOR MAPPING")
    print("-" * 60)

    cursor.execute(
        """
        SELECT
            av.vector_id,
            a.filename,
            av.content_type
        FROM asset_vectors av
        JOIN assets a
            ON av.asset_id = a.id
        ORDER BY av.vector_id
        """
    )

    mappings = cursor.fetchall()

    for mapping in mappings:

        print(
            f"Vector {mapping['vector_id']} "
            f"→ {mapping['filename']} "
            f"({mapping['content_type']})"
        )

    connection.close()

    print()
    print("=" * 60)
    print("MIGRATION COMPLETED")
    print("=" * 60)
    print(f"Migrated : {migrated}")
    print(f"Skipped  : {skipped}")
    print()


if __name__ == "__main__":
    migrate_existing_vectors()
