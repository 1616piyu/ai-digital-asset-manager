import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "./storage/database.db"
)


def get_connection():

    database_file = Path(DATABASE_PATH)

    database_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        database_file
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------
    # ASSETS TABLE
    # --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            extension TEXT NOT NULL,
            file_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            modified_time REAL NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ai_description TEXT,
            embedding_status TEXT,
            vector_id INTEGER
        )
        """
    )

    # --------------------------------------------------
    # MIGRATE OLD ASSETS TABLE
    # --------------------------------------------------

    columns = cursor.execute(
        "PRAGMA table_info(assets)"
    ).fetchall()

    column_names = {
        column["name"]
        for column in columns
    }

    if "ai_description" not in column_names:

        cursor.execute(
            """
            ALTER TABLE assets
            ADD COLUMN ai_description TEXT
            """
        )

    if "embedding_status" not in column_names:

        cursor.execute(
            """
            ALTER TABLE assets
            ADD COLUMN embedding_status TEXT
            """
        )

    if "vector_id" not in column_names:

        cursor.execute(
            """
            ALTER TABLE assets
            ADD COLUMN vector_id INTEGER
            """
        )

    # --------------------------------------------------
    # ASSET VECTORS TABLE
    # --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS asset_vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            vector_id INTEGER NOT NULL UNIQUE,
            content_type TEXT,
            content_text TEXT,
            timestamp_seconds REAL,
            FOREIGN KEY(asset_id)
                REFERENCES assets(id)
        )
        """
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    connection.commit()

    connection.close()
