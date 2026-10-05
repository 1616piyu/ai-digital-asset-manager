# Architecture and Data Flow

## 1. Overview

The AI-Powered Digital Asset Management system is a local multimodal search system designed to index images, videos and PDF documents and retrieve relevant assets using natural-language queries.

The system uses:

- SQLite for persistent asset metadata
- FAISS for vector similarity search
- Ollama for local AI inference
- LLaVA for image/video-frame understanding
- Nomic Embed Text for semantic embeddings
- PyMuPDF for PDF text extraction
- OpenCV for video processing
- Streamlit for the user interface

---

# 2. High-Level Architecture

```text
                         LOCAL DATASET
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
           Images          Videos           PDFs
              |               |               |
              v               v               v
           LLaVA          OpenCV           PyMuPDF
              |          Frame Sampling       |
              |               |               |
              |             LLaVA             |
              |               |               |
              +---------------+---------------+
                              |
                              v
                    Content Representation
                              |
                              v
                     Nomic Embed Text
                              |
                              v
                         Embeddings
                              |
                              v
                    +------------------+
                    |      FAISS       |
                    | Vector Search    |
                    +------------------+
                              |
                              |
                    +------------------+
                    |      SQLite      |
                    | Metadata/Mapping |
                    +------------------+
                              |
                              v
                       Search Engine
                              |
                              v
                       Streamlit UI
```

---

# 3. Ingestion Flow

The ingestion pipeline begins by scanning the configured dataset directory.

Each supported file is registered in SQLite with metadata such as:

- Filename
- Original path
- File extension
- File type
- File size
- Modification time
- File hash
- Processing status

The file hash is used to detect duplicates.

The ingestion system also detects whether an asset is:

- New
- Unchanged
- Modified
- Deleted
- Duplicate

This allows subsequent indexing runs to avoid unnecessarily processing unchanged assets.

---

# 4. Image Processing

Images are processed using the local LLaVA 7B vision-language model through Ollama.

The image is converted into a representation that can be described by the model.

LLaVA generates a searchable natural-language description containing concepts such as:

- People
- Animals
- Objects
- Activities
- Environment
- Vehicles
- Buildings
- Technology
- Sports
- Construction-related content

The description is then converted into a vector using Nomic Embed Text.

The vector is normalized and stored in FAISS.

The description and asset metadata remain stored in SQLite.

### Image Flow

```text
Image
  |
  v
LLaVA
  |
  v
AI Description
  |
  v
Nomic Embed Text
  |
  v
768-dimensional embedding
  |
  v
Normalized vector
  |
  v
FAISS
  |
  v
SQLite mapping
```

---

# 5. Video Processing

Processing every frame of every video is unnecessarily expensive for a local system.

Therefore, the system uses representative frame sampling.

The number of sampled frames is adapted to the video duration.

Current approach:

| Duration | Representative Frames |
|---|---:|
| Up to 10 seconds | 3 |
| 10–30 seconds | 5 |
| 30–60 seconds | 8 |
| More than 60 seconds | Up to 10 |

Each sampled frame is sent to LLaVA for visual understanding.

The resulting description is embedded using Nomic Embed Text.

The vector is stored in FAISS and mapped to the original video and timestamp in SQLite.

### Video Flow

```text
Video
  |
  v
OpenCV
  |
  v
Representative Frames
  |
  v
LLaVA
  |
  v
Frame Description
  |
  v
Nomic Embed Text
  |
  v
Embedding
  |
  v
FAISS
  |
  v
SQLite
  |
  v
Video + Timestamp
```

This approach reduces the amount of expensive vision inference required while still allowing users to search for content occurring within videos.

---

# 6. PDF Processing

PDF files are processed using PyMuPDF.

The system extracts text from each page.

Large documents are divided into overlapping chunks so that individual sections can be retrieved independently.

Each chunk is embedded using Nomic Embed Text.

The vector is stored in FAISS and associated with:

- PDF asset
- Chunk content
- Chunk type

This allows natural-language queries to retrieve relevant document content.

### PDF Flow

```text
PDF
 |
 v
PyMuPDF
 |
 v
Text Extraction
 |
 v
Text Chunking
 |
 v
Nomic Embed Text
 |
 v
Embedding
 |
 v
FAISS
 |
 v
SQLite
```

---

# 7. Semantic Search

When a user enters a natural-language query, the query is passed to the same embedding model used for indexed content.

The resulting query vector is normalized and searched against the FAISS index.

FAISS returns the nearest vectors and similarity scores.

The vector IDs are mapped back to the corresponding SQLite records.

The application then retrieves the asset metadata and displays ranked results.

### Search Flow

```text
User Query
    |
    v
Nomic Embed Text
    |
    v
Query Embedding
    |
    v
Vector Normalization
    |
    v
FAISS Similarity Search
    |
    v
Nearest Vector IDs
    |
    v
SQLite Metadata Lookup
    |
    v
Ranked Results
    |
    v
Streamlit UI
```

---

# 8. Vector Search

The system currently uses:

```text
FAISS IndexFlatIP
```

with 768-dimensional embeddings.

Embeddings are L2-normalized before insertion and search.

Therefore, the inner-product similarity behaves similarly to cosine similarity for the normalized vectors.

This provides a simple local vector-search implementation without requiring a separate vector database server.

---

# 9. Persistent Storage

SQLite stores persistent metadata and relationships between assets and vector records.

The main asset table contains information such as:

```text
assets
├── id
├── filename
├── path
├── extension
├── file_type
├── size_bytes
├── modified_time
├── file_hash
├── status
├── error_message
├── ai_description
├── embedding_status
└── vector_id
```

The vector mapping table stores:

```text
asset_vectors
├── id
├── asset_id
├── vector_id
├── content_type
├── content_text
└── timestamp