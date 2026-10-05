import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from app.database.database import (
    initialize_database,
    get_connection
)

from app.processors.image_processor import (
    describe_image
)

from app.embeddings.ollama_embeddings import (
    create_embedding
)

from app.search.vector_store import (
    load_index,
    add_vector,
    save_index
)


# ============================================================
# IMAGE INDEXER
# ============================================================

def process_images():

    print()
    print("=" * 60)
    print("IMAGE AI INDEXER")
    print("=" * 60)
    print()

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # IMPORTANT
    # ========================================================
    #
    # We intentionally select ALL images.
    #
    # Why?
    #
    # The LLaVA prompt was changed.
    # Therefore existing AI descriptions are outdated.
    #
    # We need to regenerate:
    #
    # image
    #   ↓
    # new LLaVA description
    #   ↓
    # new embedding
    #
    # ========================================================

    cursor.execute(
        """
        SELECT
            assets.id,
            assets.filename,
            assets.path
        FROM assets
        WHERE assets.file_type = 'image'
        ORDER BY assets.id
        """
    )

    assets = cursor.fetchall()


    if not assets:

        print("No images found.")

        connection.close()

        return


    print(
        f"Images to re-process: {len(assets)}"
    )

    print()


    # ========================================================
    # IMPORTANT
    # ========================================================
    #
    # We should NOT append new image vectors to the existing
    # FAISS index.
    #
    # The cleanest approach is:
    #
    # 1. regenerate image descriptions
    # 2. store them in SQLite
    # 3. rebuild FAISS afterward
    #
    # Therefore this script does NOT add vectors to FAISS.
    #
    # FAISS will be rebuilt using rebuild_index.py.
    #
    # ========================================================

    processed = 0
    failed = 0


    # ========================================================
    # PROCESS EACH IMAGE
    # ========================================================

    for asset in assets:

        asset_id = asset["id"]

        filename = asset["filename"]

        image_path = asset["path"]


        print(
            f"[PROCESSING] {filename}"
        )


        try:

            # ------------------------------------------------
            # STEP 1
            # Generate NEW AI description
            # ------------------------------------------------

            description = describe_image(
                image_path
            )


            print(
                "  AI description: generated ✓"
            )


            # ------------------------------------------------
            # STEP 2
            # Store description
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE assets
                SET
                    ai_description = ?,
                    embedding_status = ?,
                    vector_id = NULL,
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    description,
                    "pending",
                    asset_id
                )
            )


            # ------------------------------------------------
            # STEP 3
            # Save immediately
            # ------------------------------------------------

            connection.commit()


            processed += 1


            print(
                "  Description saved ✓"
            )

            print()


        except Exception as error:

            failed += 1


            # ----------------------------------------------
            # Roll back failed transaction
            # ----------------------------------------------

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
                    asset_id
                )
            )


            connection.commit()


            print(
                f"  ERROR: {error}"
            )

            print()


    connection.close()


    # ========================================================
    # SUMMARY
    # ========================================================

    print("=" * 60)
    print("IMAGE DESCRIPTION RE-INDEX SUMMARY")
    print("=" * 60)

    print(
        f"Found       : {len(assets)}"
    )

    print(
        f"Processed   : {processed}"
    )

    print(
        f"Failed      : {failed}"
    )

    print()

    print(
        "AI descriptions have been updated."
    )

    print(
        "Next step: rebuild FAISS."
    )

    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_images()