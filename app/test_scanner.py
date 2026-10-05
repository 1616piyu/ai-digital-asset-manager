from ingestion.scanner import scan_folder


DATASET_PATH = "./dataset"


def main():

    print()
    print("=" * 50)
    print("AI DIGITAL ASSET MANAGER")
    print("File Scanner")
    print("=" * 50)

    print()
    print(f"Scanning dataset: {DATASET_PATH}")
    print()

    files = scan_folder(DATASET_PATH)

    image_count = 0
    video_count = 0
    pdf_count = 0

    for file in files:

        if file["type"] == "image":
            image_count += 1

        elif file["type"] == "video":
            video_count += 1

        elif file["type"] == "pdf":
            pdf_count += 1

    print(f"Total supported files : {len(files)}")
    print(f"Images                : {image_count}")
    print(f"Videos                : {video_count}")
    print(f"PDFs                  : {pdf_count}")

    print()
    print("-" * 50)
    print("FILES")
    print("-" * 50)

    for file in files:

        size_mb = file["size_bytes"] / (1024 * 1024)

        print(
            f'{file["type"]:7} | '
            f'{file["filename"]:30} | '
            f'{size_mb:8.2f} MB'
        )


if __name__ == "__main__":
    main()
    