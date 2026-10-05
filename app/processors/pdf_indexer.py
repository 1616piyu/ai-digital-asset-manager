import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import (
    initialize_database,
    get_connection
)

from app.processors.pdf_processor import (
    create_pdf_description,
    chunk_text
)

from app.embeddings.ollama_embeddings import (
    create_embedding
)

from app.search.vector_store import (
    load_index,
    add_vector,
    save_index
)


def process_pdfs():

    print()
    print("=" * 60)
    print("PDF AI INDEXER")
    print("=" * 60)
    print()

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # Find PDFs that need processing OR PDFs whose vector
    # mapping is missing.
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            assets.id,
            assets.filename,
            assets.path,
            assets.ai_description
        FROM assets
        WHERE
            assets.file_type = 'pdf'
            AND (
                assets.embedding_status IS NULL
                OR assets.embedding_status != 'completed'
                OR NOT EXISTS (
                    SELECT 1
                    FROM asset_vectors av
                    WHERE av.asset_id = assets.id
                )
            )
        ORDER BY assets.id
        """
    )

    assets = cursor.fetchall()

    if not assets:

        print("No PDFs need processing.")

        connection.close()

        return

    print(
        f"PDFs to process: {len(assets)}"
    )

    print()

    # Existing FAISS index
    index = load_index()

    processed = 0
    failed = 0
    total_chunks = 0

    for asset in assets:

        print(
            f"[PROCESSING] {asset['filename']}"
        )

        try:

            # -------------------------------------------------
            # Remove old vector mappings for this PDF
            # -------------------------------------------------

            cursor.execute(
                """
                DELETE FROM asset_vectors
                WHERE asset_id = ?
                """,
                (asset["id"],)
            )

            # -------------------------------------------------
            # Extract PDF text
            # -------------------------------------------------

            description = create_pdf_description(
                asset["path"]
            )

            print(
                "  Text extraction: completed"
            )

            # -------------------------------------------------
            # Split text into chunks
            # -------------------------------------------------

            chunks = chunk_text(
                description,
                chunk_size=3000,
                overlap=300
            )

            print(
                f"  Chunks: {len(chunks)}"
            )

            if not chunks:

                raise ValueError(
                    "PDF produced no searchable chunks."
                )

            first_vector_id = None

            # -------------------------------------------------
            # Process every chunk
            # -------------------------------------------------

            for chunk_number, chunk in enumerate(
                chunks,
                start=1
            ):

                print(
                    f"  [CHUNK {chunk_number}/{len(chunks)}]"
                )

                # ---------------------------------------------
                # Create embedding
                # ---------------------------------------------

                embedding = create_embedding(
                    chunk
                )

                print(
                    "    Embedding: completed"
                )

                # ---------------------------------------------
                # Add to FAISS
                # ---------------------------------------------

                vector_id = index.ntotal

                add_vector(
                    index,
                    embedding
                )

                if first_vector_id is None:
                    first_vector_id = vector_id

                # ---------------------------------------------
                # Store vector metadata
                # ---------------------------------------------

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
                        vector_id,
                        "pdf_chunk",
                        chunk,
                        None
                    )
                )

                total_chunks += 1

                print(
                    f"    Vector ID: {vector_id}"
                )

            # -------------------------------------------------
            # Update PDF
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE assets
                SET
                    ai_description = ?,
                    vector_id = ?,
                    embedding_status = ?,
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    description,
                    first_vector_id,
                    "completed",
                    asset["id"]
                )
            )

            # -------------------------------------------------
            # IMPORTANT:
            # Save after every PDF
            # -------------------------------------------------

            connection.commit()

            save_index(index)

            processed += 1

            print(
                "  PDF saved successfully ✓"
            )

            print()

        except Exception as error:

            failed += 1

            # Undo partial database work for this PDF
            connection.rollback()

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

            connection.commit()

            print(
                f"  ERROR: {error}"
            )

            print()

    connection.close()

    print("=" * 60)
    print("PDF INDEXING SUMMARY")
    print("=" * 60)

    print(
        f"Found        : {len(assets)}"
    )

    print(
        f"Processed    : {processed}"
    )

    print(
        f"Failed       : {failed}"
    )

    print(
        f"Total chunks : {total_chunks}"
    )

    print(
        f"FAISS total  : {index.ntotal}"
    )

    print()
    print("PDF indexing completed.")


if __name__ == "__main__":
    process_pdfs()