import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import (
    initialize_database,
    get_connection
)


def get_indexing_status():

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # Total assets
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM assets
        """
    )

    total_assets = cursor.fetchone()["count"]

    # ---------------------------------------------------------
    # Completed
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM assets
        WHERE embedding_status = 'completed'
        """
    )

    completed = cursor.fetchone()["count"]

    # ---------------------------------------------------------
    # Failed
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM assets
        WHERE embedding_status = 'failed'
        """
    )

    failed = cursor.fetchone()["count"]

    # ---------------------------------------------------------
    # Pending
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM assets
        WHERE
            embedding_status IS NULL
            OR embedding_status != 'completed'
        """
    )

    pending = cursor.fetchone()["count"]

    # ---------------------------------------------------------
    # Asset types
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            file_type,
            COUNT(*) AS count
        FROM assets
        GROUP BY file_type
        """
    )

    type_rows = cursor.fetchall()

    asset_types = {
        row["file_type"]: row["count"]
        for row in type_rows
    }

    # ---------------------------------------------------------
    # Vector count
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM asset_vectors
        """
    )

    vector_count = cursor.fetchone()["count"]

    connection.close()

    return {
        "total_assets": total_assets,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "asset_types": asset_types,
        "vector_count": vector_count
    }


if __name__ == "__main__":

    status = get_indexing_status()

    print()
    print("=" * 50)
    print("INDEXING STATUS")
    print("=" * 50)

    print(
        f"Total assets : {status['total_assets']}"
    )

    print(
        f"Completed    : {status['completed']}"
    )

    print(
        f"Pending      : {status['pending']}"
    )

    print(
        f"Failed       : {status['failed']}"
    )

    print(
        f"Vectors      : {status['vector_count']}"
    )

    print()
    print("Asset types:")

    for asset_type, count in status["asset_types"].items():

        print(
            f"  {asset_type:8} : {count}"
        )

    print()