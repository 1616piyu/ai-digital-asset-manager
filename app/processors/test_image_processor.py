import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import (
    initialize_database,
    get_connection
)

from app.processors.image_processor import (
    describe_image
)


def main():

    image_path = (
        PROJECT_ROOT
        / "dataset"
        / "images"
        / "cat 1.jpg"
    )

    print()
    print("=" * 50)
    print("AI IMAGE PROCESSING TEST")
    print("=" * 50)
    print()

    print("Image:")
    print(image_path)
    print()

    # Make sure database exists
    initialize_database()

    # Generate AI description
    print("Generating AI description...")
    description = describe_image(
        str(image_path)
    )

    print()
    print("AI DESCRIPTION:")
    print("-" * 50)
    print(description)
    print()

    # Save description to database
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE assets
        SET
            ai_description = ?,
            embedding_status = ?
        WHERE path = ?
        """,
        (
            description,
            "description_completed",
            str(image_path.resolve())
        )
    )

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    print("-" * 50)
    print(f"Database rows updated: {updated_rows}")
    print()
    print("AI image processing test completed.")


if __name__ == "__main__":
    main()