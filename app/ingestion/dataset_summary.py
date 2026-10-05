import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from app.ingestion.scanner import scan_folder


def format_size(size_bytes):

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    size = float(size_bytes)

    for unit in units:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def get_dataset_summary(dataset_path):

    files = scan_folder(
        dataset_path
    )

    summary = {
        "total_files": len(files),
        "total_size_bytes": 0,
        "images": 0,
        "videos": 0,
        "pdfs": 0,
        "image_size": 0,
        "video_size": 0,
        "pdf_size": 0
    }

    for file in files:

        size = file["size_bytes"]

        summary["total_size_bytes"] += size

        if file["type"] == "image":

            summary["images"] += 1
            summary["image_size"] += size

        elif file["type"] == "video":

            summary["videos"] += 1
            summary["video_size"] += size

        elif file["type"] == "pdf":

            summary["pdfs"] += 1
            summary["pdf_size"] += size

    return summary


def print_summary(summary):

    print()
    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print()
    print(
        f"Total files : "
        f"{summary['total_files']}"
    )

    print(
        f"Total size  : "
        f"{format_size(summary['total_size_bytes'])}"
    )

    print()

    print("Images")
    print(
        f"  Files : {summary['images']}"
    )
    print(
        f"  Size  : "
        f"{format_size(summary['image_size'])}"
    )

    print()

    print("Videos")
    print(
        f"  Files : {summary['videos']}"
    )
    print(
        f"  Size  : "
        f"{format_size(summary['video_size'])}"
    )

    print()

    print("PDFs")
    print(
        f"  Files : {summary['pdfs']}"
    )
    print(
        f"  Size  : "
        f"{format_size(summary['pdf_size'])}"
    )

    print()


if __name__ == "__main__":

    dataset_path = (
        PROJECT_ROOT / "dataset"
    )

    summary = get_dataset_summary(
        str(dataset_path)
    )

    print_summary(summary)