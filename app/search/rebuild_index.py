import sys
from pathlib import Path

import faiss
import numpy as np


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
    save_index
)


VECTOR_DIMENSION = 768


def rebuild_faiss_index():

    print()
    print("=" * 60)
    print("FAISS INDEX REBUILD")
    print("=" * 60)
    print()

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # CREATE A COMPLETELY NEW FAISS INDEX
    # --------------------------------------------------

    index = faiss.IndexFlatIP(
        VECTOR_DIMENSION
    )

    # --------------------------------------------------
    # GET ALL CURRENT ASSET VECTORS
    # --------------------------------------------------

    cursor.execute(
        """
        SELECT
            av.id,
            av.asset_id,
            av.vector_id,
            av.content_type,
            av.content_text,
            av.timestamp_seconds,
            a.filename

        FROM asset_vectors av

        JOIN assets a
            ON av.asset_id = a.id

        ORDER BY av.id
        """
    )

    vectors = cursor.fetchall()

    print(
        f"Vector records found: "
        f"{len(vectors)}"
    )

    print()

    # --------------------------------------------------
    # REBUILD VECTORS
    # --------------------------------------------------

    new_vector_id = 0

    for vector in vectors:

        print(
            f"[REBUILD] "
            f"{vector['filename']}"
        )

        print(
            f"  Content type: "
            f"{vector['content_type']}"
        )

        if (
            vector["timestamp_seconds"]
            is not None
        ):

            print(
                f"  Timestamp: "
                f"{vector['timestamp_seconds']:.2f}s"
            )

        try:

            # Re-create embedding from stored content
            embedding = create_embedding(
                vector["content_text"]
            )

            vector_array = np.array(
                embedding,
                dtype="float32"
            ).reshape(
                1,
                -1
            )

            # Normalize for cosine similarity
            faiss.normalize_L2(
                vector_array
            )

            # Add to new FAISS index
            index.add(
                vector_array
            )

            # Update vector ID
            cursor.execute(
                """
                UPDATE asset_vectors
                SET vector_id = ?
                WHERE id = ?
                """,
                (
                    new_vector_id,
                    vector["id"]
                )
            )

            # Keep assets.vector_id synchronized
            if vector["content_type"] == "asset":

                cursor.execute(
                    """
                    UPDATE assets
                    SET vector_id = ?
                    WHERE id = ?
                    """,
                    (
                        new_vector_id,
                        vector["asset_id"]
                    )
                )

            print(
                f"  New Vector ID: "
                f"{new_vector_id}"
            )

            new_vector_id += 1

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

    # --------------------------------------------------
    # SAVE NEW INDEX
    # --------------------------------------------------

    save_index(
        index
    )

    connection.commit()
    connection.close()

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("FAISS REBUILD COMPLETED")
    print("=" * 60)

    print(
        f"Vectors in index: "
        f"{index.ntotal}"
    )

    print()
    print(
        "Old/stale FAISS vectors have been removed."
    )

    print(
        "New vector IDs are synchronized with SQLite."
    )

    print()


if __name__ == "__main__":

    rebuild_faiss_index()