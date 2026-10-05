from pathlib import Path
import hashlib


# Supported file extensions
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm"
}

PDF_EXTENSIONS = {
    ".pdf"
}


def get_file_type(file_path: Path) -> str:
    """
    Identify the type of a file based on its extension.
    """

    extension = file_path.suffix.lower()

    if extension in IMAGE_EXTENSIONS:
        return "image"

    if extension in VIDEO_EXTENSIONS:
        return "video"

    if extension in PDF_EXTENSIONS:
        return "pdf"

    return "unsupported"


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.

    Reading the file in chunks prevents large files
    from being loaded completely into memory.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(1024 * 1024)  # 1 MB

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def scan_folder(folder_path: str) -> list[dict]:
    """
    Scan a folder recursively and return information
    about supported media files.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"Dataset folder does not exist: {folder}"
        )

    if not folder.is_dir():
        raise NotADirectoryError(
            f"Dataset path is not a directory: {folder}"
        )

    files = []

    for file_path in folder.rglob("*"):

        # Ignore directories
        if not file_path.is_file():
            continue

        file_type = get_file_type(file_path)

        # Ignore unsupported files
        if file_type == "unsupported":
            continue

        stat = file_path.stat()

        file_info = {
            "filename": file_path.name,
            "path": str(file_path.resolve()),
            "extension": file_path.suffix.lower(),
            "type": file_type,
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime,
            "hash": calculate_file_hash(file_path)
        }

        files.append(file_info)

    return files