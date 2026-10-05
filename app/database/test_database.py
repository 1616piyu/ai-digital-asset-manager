import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import initialize_database, get_connection


def main():

    print("Initializing database...")

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tables = cursor.fetchall()

    print("\nDatabase tables:")

    for table in tables:
        print("-", table["name"])

    connection.close()

    print("\nDatabase initialized successfully.")


if __name__ == "__main__":
    main()