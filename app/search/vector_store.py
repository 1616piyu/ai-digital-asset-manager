import os
from pathlib import Path

import faiss
import numpy as np


INDEX_PATH = os.getenv(
    "FAISS_INDEX_PATH",
    "./storage/faiss.index"
)

VECTOR_DIMENSION = 768


def create_index():
    """
    Create a new FAISS index.
    """

    return faiss.IndexFlatIP(
        VECTOR_DIMENSION
    )


def normalize_vector(vector):
    """
    Normalize a vector for cosine similarity.
    """

    vector = np.array(
        vector,
        dtype="float32"
    ).reshape(1, -1)

    faiss.normalize_L2(vector)

    return vector


def add_vector(index, vector):
    """
    Add one normalized embedding to FAISS.
    """

    normalized = normalize_vector(
        vector
    )

    index.add(normalized)


def save_index(index):
    """
    Save FAISS index to disk.
    """

    index_path = Path(INDEX_PATH)

    index_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(index_path)
    )


def load_index():
    """
    Load an existing FAISS index.
    """

    index_path = Path(INDEX_PATH)

    if not index_path.exists():
        return create_index()

    return faiss.read_index(
        str(index_path)
    )


def search_index(
    index,
    query_vector,
    top_k=10
):
    """
    Search FAISS using cosine similarity.
    """

    normalized = normalize_vector(
        query_vector
    )

    scores, indices = index.search(
        normalized,
        top_k
    )

    return scores[0], indices[0]