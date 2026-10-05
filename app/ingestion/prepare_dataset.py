from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "dataset"


FOLDERS = [
    DATASET_DIR / "images" / "animals",
    DATASET_DIR / "images" / "people",
    DATASET_DIR / "images" / "buildings",
    DATASET_DIR / "images" / "nature",
    DATASET_DIR / "images" / "vehicles",
    DATASET_DIR / "images" / "food",
    DATASET_DIR / "images" / "technology",
    DATASET_DIR / "images" / "sports",

    DATASET_DIR / "videos" / "sports",
    DATASET_DIR / "videos" / "construction",
    DATASET_DIR / "videos" / "people",
    DATASET_DIR / "videos" / "vehicles",
    DATASET_DIR / "videos" / "nature",

    DATASET_DIR / "pdfs" / "brochures",
    DATASET_DIR / "pdfs" / "reports",
    DATASET_DIR / "pdfs" / "documents",
]


def prepare_dataset():

    print()
    print("=" * 60)
    print("DATASET DIRECTORY PREPARATION")
    print("=" * 60)
    print()

    created = 0

    for folder in FOLDERS:

        if not folder.exists():

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            print(
                f"[CREATED] {folder.relative_to(PROJECT_ROOT)}"
            )

            created += 1

        else:

            print(
                f"[EXISTS]  {folder.relative_to(PROJECT_ROOT)}"
            )

    print()
    print("=" * 60)

    print(
        f"Folders created : {created}"
    )

    print(
        f"Total folders   : {len(FOLDERS)}"
    )

    print()
    print("Dataset structure is ready.")


if __name__ == "__main__":
    prepare_dataset()