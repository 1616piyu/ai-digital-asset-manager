import pymupdf
from pathlib import Path


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract searchable text from a PDF.
    """

    pdf_path = Path(pdf_path)

    document = pymupdf.open(pdf_path)

    pages = []

    for page in document:
        text = page.get_text()

        if text.strip():
            pages.append(text.strip())

    document.close()

    return "\n\n".join(pages)


def create_pdf_description(pdf_path: str) -> str:
    """
    Extract searchable PDF text.
    """

    text = extract_pdf_text(pdf_path)

    if not text:
        return "PDF contains no extractable text."

    # Keep metadata reasonably sized.
    return text[:20000]


def chunk_text(
    text: str,
    chunk_size: int = 3000,
    overlap: int = 300
) -> list[str]:
    """
    Split long PDF text into overlapping chunks.

    Overlap helps preserve context between chunks.
    """

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


if __name__ == "__main__":

    pdf_path = (
        "dataset/pdfs/"
        "Piyush_Pratap_Singh_Dream11_AI_Projects_Portfolio.pdf"
    )

    print()
    print("=" * 60)
    print("PDF TEXT EXTRACTION TEST")
    print("=" * 60)
    print()

    description = create_pdf_description(pdf_path)

    chunks = chunk_text(description)

    print(f"Characters : {len(description)}")
    print(f"Chunks     : {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):

        print()
        print(f"--- Chunk {index} ---")
        print(chunk[:500])

    print()
    print("=" * 60)
    print("PDF extraction completed.")
    print("=" * 60)
