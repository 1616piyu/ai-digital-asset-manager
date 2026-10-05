import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from app.database.database import (
    get_connection
)

from app.embeddings.ollama_embeddings import (
    create_embedding
)

from app.search.vector_store import (
    load_index,
    search_index
)


def semantic_search(
    query: str,
    top_k: int = 5
):
    """
    Perform semantic search across images,
    PDFs and videos.

    FAISS vector IDs are mapped through
    the asset_vectors table.
    """

    # --------------------------------------------------
    # CREATE QUERY EMBEDDING
    # --------------------------------------------------

    query_embedding = create_embedding(
        query
    )

    # --------------------------------------------------
    # LOAD FAISS
    # --------------------------------------------------

    index = load_index()

    if index.ntotal == 0:
        return []

    top_k = min(
        top_k,
        index.ntotal
    )

    scores, vector_ids = search_index(
        index,
        query_embedding,
        top_k
    )

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    results = []

    # --------------------------------------------------
    # MAP VECTOR → ASSET
    # --------------------------------------------------

    for score, vector_id in zip(
        scores,
        vector_ids
    ):

        if vector_id < 0:
            continue

        cursor.execute(
            """
            SELECT
                av.vector_id,
                av.content_type,
                av.content_text,
                av.timestamp_seconds,

                a.id,
                a.filename,
                a.path,
                a.file_type,
                a.size_bytes

            FROM asset_vectors av

            JOIN assets a
                ON av.asset_id = a.id

            WHERE av.vector_id = ?
            """,
            (
                int(vector_id),
            )
        )

        asset = cursor.fetchone()

        if asset is None:
            continue

        results.append(
            {
                "id": asset["id"],

                "filename": asset["filename"],

                "path": asset["path"],

                "file_type": asset["file_type"],

                "size_bytes": asset["size_bytes"],

                "description": asset[
                    "content_text"
                ],

                "score": float(score),

                "vector_id": asset[
                    "vector_id"
                ],

                "content_type": asset[
                    "content_type"
                ],

                "timestamp_seconds": asset[
                    "timestamp_seconds"
                ]
            }
        )

    connection.close()

    return results