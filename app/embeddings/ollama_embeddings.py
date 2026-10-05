import requests


OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    """
    Convert text into a semantic embedding using Ollama.
    """

    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["embedding"]