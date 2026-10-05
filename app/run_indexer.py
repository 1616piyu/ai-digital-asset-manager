import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.indexer import index_files


DATASET_PATH = "./dataset"


def main():

    print("=" * 50)
    print("AI DIGITAL ASSET MANAGER")
    print("INDEXER")
    print("=" * 50)

    index_files(DATASET_PATH)


if __name__ == "__main__":
    main()