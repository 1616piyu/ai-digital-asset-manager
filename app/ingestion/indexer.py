import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from app.ingestion.scanner import scan_folder

from app.database.database import (
    initialize_database,
    get_connection
)


def index_files(dataset_path: str):

    print()
    print("=" * 50)
    print("INCREMENTAL INDEXING")
    print("=" * 50)
    print()

    initialize_database()

    files = scan_folder(
        dataset_path
    )

    print(
        f"Found {len(files)} supported files.\n"
    )

    connection = get_connection()
    cursor = connection.cursor()

    new_files = 0
    unchanged_files = 0
    modified_files = 0
    duplicate_files = 0
    failed_files = 0

    for file in files:

        try:

            # ------------------------------------------
            # CHECK WHETHER PATH ALREADY EXISTS
            # ------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    file_hash,
                    status
                FROM assets
                WHERE path = ?
                """,
                (
                    file["path"],
                )
            )

            existing = cursor.fetchone()

            # ------------------------------------------
            # NEW FILE
            # ------------------------------------------

            if existing is None:

                # Check duplicate content
                cursor.execute(
                    """
                    SELECT
                        id,
                        path
                    FROM assets
                    WHERE file_hash = ?
                    """,
                    (
                        file["hash"],
                    )
                )

                duplicate = cursor.fetchone()

                if duplicate is not None:

                    duplicate_files += 1

                    print(
                        f"[DUPLICATE] "
                        f"{file['filename']} "
                        f"(same content as "
                        f"{duplicate['path']})"
                    )

                    continue

                cursor.execute(
                    """
                    INSERT INTO assets (
                        filename,
                        path,
                        extension,
                        file_type,
                        size_bytes,
                        modified_time,
                        file_hash,
                        status,
                        embedding_status,
                        vector_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        file["filename"],
                        file["path"],
                        file["extension"],
                        file["type"],
                        file["size_bytes"],
                        file["modified_time"],
                        file["hash"],
                        "pending",
                        None,
                        None
                    )
                )

                new_files += 1

                print(
                    f"[NEW] "
                    f"{file['type']:7} "
                    f"{file['filename']}"
                )

                continue

            # ------------------------------------------
            # UNCHANGED FILE
            # ------------------------------------------

            if existing["file_hash"] == file["hash"]:

                unchanged_files += 1

                print(
                    f"[UNCHANGED] "
                    f"{file['filename']}"
                )

                continue

            # ------------------------------------------
            # MODIFIED FILE
            # ------------------------------------------

            # Remove old vector mappings for this asset
            cursor.execute(
                """
                DELETE FROM asset_vectors
                WHERE asset_id = ?
                """,
                (
                    existing["id"],
                )
            )

            cursor.execute(
                """
                UPDATE assets
                SET
                    filename = ?,
                    extension = ?,
                    file_type = ?,
                    size_bytes = ?,
                    modified_time = ?,
                    file_hash = ?,
                    status = ?,
                    embedding_status = ?,
                    ai_description = ?,
                    vector_id = ?,
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    file["filename"],
                    file["extension"],
                    file["type"],
                    file["size_bytes"],
                    file["modified_time"],
                    file["hash"],
                    "pending",
                    None,
                    None,
                    None,
                    existing["id"]
                )
            )

            modified_files += 1

            print(
                f"[MODIFIED] "
                f"{file['filename']} "
                f"→ marked for reprocessing"
            )

        except Exception as error:

            failed_files += 1

            print(
                f"[ERROR] "
                f"{file['filename']}: "
                f"{error}"
            )

    # ------------------------------------------
    # HANDLE DELETED FILES
    # ------------------------------------------

    scanned_paths = {
        file["path"]
        for file in files
    }

    cursor.execute(
        """
        SELECT
            id,
            filename,
            path
        FROM assets
        """
    )

    database_assets = cursor.fetchall()

    deleted_files = 0

    for asset in database_assets:

        if asset["path"] not in scanned_paths:

            # Remove vector mappings
            cursor.execute(
                """
                DELETE FROM asset_vectors
                WHERE asset_id = ?
                """,
                (
                    asset["id"],
                )
            )

            # Remove asset record
            cursor.execute(
                """
                DELETE FROM assets
                WHERE id = ?
                """,
                (
                    asset["id"],
                )
            )

            deleted_files += 1

            print(
                f"[DELETED] "
                f"{asset['filename']}"
            )

    connection.commit()
    connection.close()

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    print()
    print("=" * 50)
    print("INDEXING SUMMARY")
    print("=" * 50)

    print(
        f"Total scanned : "
        f"{len(files)}"
    )

    print(
        f"New files     : "
        f"{new_files}"
    )

    print(
        f"Unchanged     : "
        f"{unchanged_files}"
    )

    print(
        f"Modified      : "
        f"{modified_files}"
    )

    print(
        f"Deleted       : "
        f"{deleted_files}"
    )

    print(
        f"Duplicates    : "
        f"{duplicate_files}"
    )

    print(
        f"Failed        : "
        f"{failed_files}"
    )

    print()
    print(
        "Incremental indexing completed."
    )


if __name__ == "__main__":

    index_files(
        "./dataset"
    )