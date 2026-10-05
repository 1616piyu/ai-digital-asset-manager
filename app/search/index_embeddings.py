import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import (
    initialize_database,
    get_connection
)

from app.embeddings.ollama_embeddings import (
    create_embedding
)

from app.search.vector_store import (
    load_index,
    add_vector,
    save_index
)


def index_asset_embeddings():

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # Get assets that have an AI description
    # but don't have an embedding yet.
    cursor.execute(
        """
        SELECT
            id,
            filename,
            ai_description
        FROM assets
        WHERE
            ai_description IS NOT NULL
            AND ai_description != ''
            AND vector_id IS NULL
        ORDER BY id
        """
    )

    assets = cursor.fetchall()

    if not assets:
        print("No assets need embedding.")
        connection.close()
        return

    print()
    print("=" * 50)
    print("EMBEDDING INDEXER")
    print("=" * 50)
    print()

    # Load existing FAISS index
    index = load_index()

    for asset in assets:

        print(
            f"Creating embedding: "
            f"{asset['filename']}"
        )

        try:

            # Create semantic embedding
            embedding = create_embedding(
                asset["ai_description"]
            )

            # Current FAISS position
            vector_id = index.ntotal

            # Add vector
            add_vector(
                index,
                embedding
            )

            # Save vector ID in SQLite
            cursor.execute(
                """
                UPDATE assets
                SET
                    vector_id = ?,
                    embedding_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    vector_id,
                    "completed",
                    asset["id"]
                )
            )

            print(
                f"  Vector ID: {vector_id}"
            )

            print(
                "  Status: completed"
            )

        except Exception as error:

            cursor.execute(
                """
                UPDATE assets
                SET
                    embedding_status = ?,
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    "failed",
                    str(error),
                    asset["id"]
                )
            )

            print(
                f"  ERROR: {error}"
            )

    # Save FAISS index
    save_index(index)

    connection.commit()
    connection.close()

    print()
    print("=" * 50)
    print("EMBEDDING INDEXING COMPLETED")
    print("=" * 50)
    print(
        f"Total vectors: {index.ntotal}"
    )


if __name__ == "__main__":
    index_asset_embeddings()