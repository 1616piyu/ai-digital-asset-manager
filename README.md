# AI-Powered Digital Asset Management & Semantic Search

An AI-powered local Digital Asset Management (DAM) system that allows users to search images, videos, and PDF documents using natural-language queries.

Instead of relying only on filenames or folders, the system uses AI-generated descriptions and vector embeddings to understand the content of digital assets and return semantically relevant results.

---

## Demo

**Demo video:** _Add your demo video link here before submission._

**GitHub Repository:**  
https://github.com/1616piyu/ai-digital-asset-manager

---

## Problem Statement

Large collections of digital assets become difficult to search when files are distributed across folders and filenames do not describe their actual content.

For example, a user may want to find:

- "A woman standing with a cat"
- "Workers at a construction site"
- "Customer testimonial videos"
- "Brochures related to residential projects"
- "Images showing a modern living room"
- "Videos containing construction activity"

Traditional filename-based search cannot reliably answer these queries.

This project provides a semantic search layer over a local collection of images, videos, and PDFs.

---

## Key Features

### Multimodal Asset Ingestion

Supports:

- Images
- Videos
- PDF documents

The system scans a local dataset, identifies supported files, extracts metadata, processes the content, and indexes it for semantic search.

### AI Content Understanding

Images and sampled video frames are analyzed using a locally running vision-language model.

PDF documents are processed using text extraction.

### Semantic Search

Users can enter natural-language queries such as:

```text
a cricket match

people in a stadium

a cute kitten

workers at a construction site

AI and machine learning projects
```

The query is converted into an embedding and compared with indexed asset embeddings using FAISS.

### Ranked Results

Search results include:

- Asset filename
- Asset type
- Semantic relevance score
- AI-generated description/content
- Original file path
- Video timestamp where applicable
- Preview/open-original functionality

### Video Frame Sampling

Videos are not processed frame-by-frame.

Representative frames are sampled across the video duration using adaptive sampling:

| Video duration | Sampled frames |
|---|---:|
| ≤ 10 seconds | 3 |
| 10–30 seconds | 5 |
| 30–60 seconds | 8 |
| > 60 seconds | 10 |

This reduces processing cost while still providing searchable video content.

### PDF Chunking

PDF text is extracted and divided into chunks before embedding.

This allows long documents to be represented by multiple searchable semantic sections rather than a single large embedding.

### Incremental Indexing

The ingestion pipeline tracks:

- File hash
- File size
- Modification time
- Processing status
- Embedding status

Unchanged files can be skipped during later indexing runs.

Modified files can be reprocessed.

Deleted files are removed from the metadata/vector mapping.

Duplicate files are detected using file hashes.

### Failure Handling

The indexing pipeline records failures at the asset level and continues processing other files.

This prevents one corrupted or unsupported file from stopping the entire ingestion process.

### Persistent Storage

The system uses:

- **SQLite** for asset metadata and vector mappings
- **FAISS** for vector similarity search

The database stores relationships between assets and their vector IDs.

### Streamlit Interface

The Streamlit interface provides:

- Search box
- Asset-type filters
- Top-K control
- Minimum relevance score
- Image previews
- Video previews
- PDF previews
- Semantic relevance scores
- Video timestamps
- AI descriptions
- Original file location

---

## Architecture

```text
                    ┌──────────────────────┐
                    │     Local Dataset    │
                    │ Images / Videos / PDF │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      File Scanner     │
                    │ Metadata + File Hash  │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       ┌───────────┐     ┌───────────┐     ┌───────────┐
       │  Images   │     │  Videos   │     │   PDFs    │
       └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
             │                 │                 │
             ▼                 ▼                 ▼
        LLaVA Vision     Frame Sampling      PyMuPDF
             │                 │                 │
             ▼                 ▼                 ▼
       AI Description    Frame Description   Text Chunks
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │  nomic-embed-text    │
                    │  768-d Embeddings    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │        FAISS         │
                    │  Vector Similarity   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       SQLite         │
                    │ Metadata + Mapping   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Search Engine    │
                    │ Query → Embedding    │
                    │ → FAISS → Ranking    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Streamlit UI      │
                    │ Ranked Search Results│
                    └──────────────────────┘
```

For the detailed architecture and processing flow, see:

- [Architecture Documentation](docs/architecture.md)
- [Search Evaluation](docs/search_evaluation.md)
- [Dataset Notes](docs/dataset_notes.md)

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| UI | Streamlit |
| Vision-Language Model | Ollama + LLaVA 7B |
| Embedding Model | Ollama + nomic-embed-text |
| Embedding Dimension | 768 |
| Vector Search | FAISS |
| Database | SQLite |
| Image Processing | OpenCV / Pillow |
| Video Processing | OpenCV |
| PDF Processing | PyMuPDF |
| Numerical Processing | NumPy |
| ML / Data Processing | scikit-learn / pandas |
| Environment | Local Windows machine |

---

## Project Structure

```text
ai-digital-asset-manager/
│
├── app/
│   ├── database/
│   │   ├── database.py
│   │   ├── status.py
│   │   └── test_database.py
│   │
│   ├── embeddings/
│   │   └── ollama_embeddings.py
│   │
│   ├── ingestion/
│   │   ├── dataset_summary.py
│   │   ├── indexer.py
│   │   ├── prepare_dataset.py
│   │   ├── reindex_pipeline.py
│   │   └── scanner.py
│   │
│   ├── processors/
│   │   ├── image_indexer.py
│   │   ├── image_processor.py
│   │   ├── pdf_indexer.py
│   │   ├── pdf_processor.py
│   │   ├── video_indexer.py
│   │   └── video_processor.py
│   │
│   ├── search/
│   │   ├── index_embeddings.py
│   │   ├── migrate_vectors.py
│   │   ├── rebuild_index.py
│   │   ├── search_engine.py
│   │   ├── test_search.py
│   │   └── vector_store.py
│   │
│   └── ui/
│       └── app.py
│
├── docs/
│   ├── architecture.md
│   ├── dataset_notes.md
│   └── search_evaluation.md
│
├── tests/
│   └── evaluate_search.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Dataset

The project was evaluated using a locally collected multimodal dataset.

### Current dataset summary

| Asset type | Files | Size |
|---|---:|---:|
| Images | 135 | ~292 MB |
| Videos | 85 | ~3.10 GB |
| PDFs | 14 | ~120 MB |
| **Total** | **234** | **~3.50 GB** |

After duplicate detection and incremental indexing, the metadata database contains **229 unique assets**.

The dataset includes categories such as:

- Animals
- Buildings
- Food
- Nature
- People
- Sports
- Technology
- Vehicles
- Construction
- Brochures
- Reports
- Documents

The dataset itself is intentionally **not included in this GitHub repository** because of its size and source/licensing considerations.

Dataset documentation is available in:

- [Dataset Notes](docs/dataset_notes.md)
- [Dataset Sources](docs/dataset_sources.csv)

---

## Dataset Limitation

The assignment recommends a dataset in the 5–10 GB range.

The current working dataset is approximately **3.5 GB** rather than the full 5–10 GB target because local processing time, storage, and AI inference constraints were considered during development.

The system architecture is designed to scale beyond the current dataset through:

- Incremental indexing
- File hashing
- Duplicate detection
- Adaptive video sampling
- Persistent
