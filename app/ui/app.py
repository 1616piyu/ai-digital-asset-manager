# ============================================================
# AI DIGITAL ASSET MANAGER - STREAMLIT UI
# ============================================================

import sys
from pathlib import Path

# ============================================================
# IMPORTANT: PROJECT ROOT
# ============================================================

# app/ui/app.py
# parents[0] = app/ui
# parents[1] = app
# parents[2] = project root

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Force project root to the beginning of Python's import path
project_root_string = str(PROJECT_ROOT)

if project_root_string in sys.path:
    sys.path.remove(project_root_string)

sys.path.insert(0, project_root_string)


# ============================================================
# NOW IMPORT PROJECT MODULES
# ============================================================

import webbrowser

import streamlit as st

from app.database.status import get_indexing_status
from app.search.search_engine import semantic_search


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Digital Asset Manager",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    .asset-card {
        padding: 1rem;
        border: 1px solid #dddddd;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 AI Digital Asset Manager</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Search images, videos and PDFs using natural language.
    AI understands the content of your assets instead of relying
    only on filenames.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# INDEX STATUS
# ============================================================

try:

    status = get_indexing_status()

    total_assets = status.get("total_assets", 0)
    completed = status.get("completed", 0)
    pending = status.get("pending", 0)
    failed = status.get("failed", 0)
    vectors = status.get("vectors", 0)

except Exception as error:

    total_assets = 0
    completed = 0
    pending = 0
    failed = 0
    vectors = 0

    st.warning(
        f"Could not load indexing status: {error}"
    )


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Assets",
        total_assets
    )

with col2:
    st.metric(
        "Indexed",
        completed
    )

with col3:
    st.metric(
        "Pending",
        pending
    )

with col4:
    st.metric(
        "Search Vectors",
        vectors
    )


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔍 Search Filters")


file_type = st.sidebar.selectbox(
    "Asset Type",
    [
        "All",
        "image",
        "video",
        "pdf"
    ]
)


top_k = st.sidebar.slider(
    "Results to display",
    min_value=3,
    max_value=15,
    value=8
)


min_score = st.sidebar.slider(
    "Minimum relevance",
    min_value=0.30,
    max_value=0.80,
    value=0.45,
    step=0.05
)


# ============================================================
# SIDEBAR STATUS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("📊 Index Status")

st.sidebar.write(
    f"**Total assets:** {total_assets}"
)

st.sidebar.write(
    f"**Indexed:** {completed}"
)

st.sidebar.write(
    f"**Pending:** {pending}"
)

st.sidebar.write(
    f"**Failed:** {failed}"
)

st.sidebar.write(
    f"**Vectors:** {vectors}"
)


# ============================================================
# SUPPORTED ASSETS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("Supported Assets")

st.sidebar.write("🖼️ Images")
st.sidebar.write("🎬 Videos")
st.sidebar.write("📄 PDFs")


# ============================================================
# AI PIPELINE
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("AI Pipeline")

st.sidebar.caption(
    "👁️ LLaVA 7B — visual understanding"
)

st.sidebar.caption(
    "🧠 nomic-embed-text — embeddings"
)

st.sidebar.caption(
    "⚡ FAISS — semantic vector search"
)

st.sidebar.caption(
    "🗄️ SQLite — metadata"
)

st.sidebar.caption(
    "🐍 Python + Streamlit"
)


# ============================================================
# SEARCH INPUT
# ============================================================

query = st.text_input(
    "Search your digital assets",
    placeholder=(
        "Example: workers at a construction site"
    )
)


search_button = st.button(
    "🔍 Search Assets",
    type="primary",
    use_container_width=True
)


# ============================================================
# EXAMPLE SEARCHES
# ============================================================

st.markdown(
    "### Try natural-language searches"
)

example_queries = [
    "construction activity",
    "workers at a construction site",
    "sports event with spectators",
    "cricket match",
    "technology devices",
    "people using technology",
    "a cute kitten",
    "cars and vehicles",
    "nature landscape",
    "data analytics documents",
    "annual report",
    "brochure"
]


example_columns = st.columns(4)


for index, example in enumerate(example_queries):

    with example_columns[index % 4]:

        st.caption(example)


# ============================================================
# SEARCH
# ============================================================

if search_button and query.strip():

    with st.spinner(
        "Searching AI-indexed assets..."
    ):

        try:

            # Retrieve more candidates first.
            #
            # This is important because we apply
            # filtering and duplicate grouping later.

            raw_results = semantic_search(
                query.strip(),
                top_k=max(
                    30,
                    top_k * 4
                )
            )

        except Exception as error:

            st.error(
                f"Search failed: {error}"
            )

            raw_results = []


    # ========================================================
    # RELEVANCE FILTER
    # ========================================================

    filtered_results = [
        result
        for result in raw_results
        if result["score"] >= min_score
    ]


    # ========================================================
    # FILE TYPE FILTER
    # ========================================================

    if file_type != "All":

        filtered_results = [
            result
            for result in filtered_results
            if result["file_type"] == file_type
        ]


    # ========================================================
    # REMOVE DUPLICATE ASSETS
    # ========================================================
    #
    # PDFs may have multiple chunks.
    #
    # Videos may have multiple frame vectors.
    #
    # We only show the actual asset once.
    # ========================================================

    unique_assets = {}


    for result in filtered_results:

        asset_id = result["id"]

        if (
            asset_id not in unique_assets
            or result["score"]
            > unique_assets[asset_id]["score"]
        ):

            unique_assets[asset_id] = result


    results = list(
        unique_assets.values()
    )


    # ========================================================
    # SORT BY RELEVANCE
    # ========================================================

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    # ========================================================
    # LIMIT RESULTS
    # ========================================================

    results = results[:top_k]


    # ========================================================
    # RESULT HEADER
    # ========================================================

    st.divider()

    st.subheader(
        f"Search Results — {len(results)} assets"
    )

    st.caption(
        f'Query: "{query.strip()}"'
    )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not results:

        st.warning(
            "No sufficiently relevant assets were found."
        )

        st.info(
            "Try a broader query or lower the "
            "Minimum relevance value."
        )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    for rank, result in enumerate(
        results,
        start=1
    ):

        file_path = Path(
            result["path"]
        )

        score = float(
            result["score"]
        )

        score_percentage = score * 100


        # ====================================================
        # RESULT CARD
        # ====================================================

        st.markdown(
            '<div class="asset-card">',
            unsafe_allow_html=True
        )


        preview_column, details_column = st.columns(
            [1, 2]
        )


        # ====================================================
        # PREVIEW
        # ====================================================

        with preview_column:

            # ------------------------------
            # IMAGE
            # ------------------------------

            if result["file_type"] == "image":

                if file_path.exists():

                    st.image(
                        str(file_path),
                        width="stretch"
                    )

                else:

                    st.info(
                        "Image unavailable"
                    )


            # ------------------------------
            # VIDEO
            # ------------------------------

            elif result["file_type"] == "video":

                if file_path.exists():

                    st.video(
                        str(file_path)
                    )

                else:

                    st.info(
                        "Video unavailable"
                    )


            # ------------------------------
            # PDF
            # ------------------------------

            elif result["file_type"] == "pdf":

                st.markdown(
                    """
                    <div style="
                        font-size: 80px;
                        text-align: center;
                        padding: 35px;
                    ">
                        📄
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ====================================================
        # DETAILS
        # ====================================================

        with details_column:

            st.markdown(
                f"### {rank}. {result['filename']}"
            )


            # ------------------------------
            # TYPE
            # ------------------------------

            if result["file_type"] == "image":

                st.write(
                    "🖼️ **IMAGE**"
                )

            elif result["file_type"] == "video":

                st.write(
                    "🎬 **VIDEO**"
                )

            else:

                st.write(
                    "📄 **PDF**"
                )


            # ------------------------------
            # RELEVANCE
            # ------------------------------

            st.progress(
                min(
                    max(score, 0.0),
                    1.0
                )
            )

            st.write(
                f"**Semantic relevance:** "
                f"{score_percentage:.1f}%"
            )


            # ------------------------------
            # VIDEO TIMESTAMP
            # ------------------------------

            timestamp = result.get(
                "timestamp_seconds"
            )

            if (
                result["file_type"] == "video"
                and timestamp is not None
            ):

                timestamp = float(
                    timestamp
                )

                minutes = int(
                    timestamp // 60
                )

                seconds = int(
                    timestamp % 60
                )

                st.write(
                    f"🎬 **Matched around:** "
                    f"{minutes}:{seconds:02d}"
                )


            # ------------------------------
            # AI DESCRIPTION
            # ------------------------------

            if result.get("description"):

                with st.expander(
                    "🤖 AI Understanding"
                ):

                    st.write(
                        result["description"]
                    )


            # ------------------------------
            # ORIGINAL LOCATION
            # ------------------------------

            st.caption(
                "Original file location"
            )

            st.code(
                result["path"],
                language=None
            )


            # ------------------------------
            # OPEN ORIGINAL
            # ------------------------------

            if file_path.exists():

                if st.button(
                    "📂 Open Original",
                    key=(
                        f"open_"
                        f"{result['id']}_"
                        f"{rank}"
                    )
                ):

                    try:

                        webbrowser.open(
                            file_path.as_uri()
                        )

                    except Exception:

                        st.info(
                            "File location: "
                            + str(file_path)
                        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# DEFAULT SCREEN
# ============================================================

else:

    st.info(
        "Enter a natural-language query to search "
        "your indexed images, videos and PDFs."
    )


    # ========================================================
    # CONSTRUCTION
    # ========================================================

    st.markdown(
        "### 🏗️ Construction"
    )

    st.write(
        "construction activity • "
        "workers at a construction site • "
        "building under construction • "
        "construction equipment"
    )


    # ========================================================
    # SPORTS
    # ========================================================

    st.markdown(
        "### 🏏 Sports"
    )

    st.write(
        "cricket match • "
        "sports event • "
        "stadium spectators • "
        "people playing sports"
    )


    # ========================================================
    # TECHNOLOGY
    # ========================================================

    st.markdown(
        "### 💻 Technology"
    )

    st.write(
        "technology devices • "
        "people using computers • "
        "electronic devices • "
        "technology projects"
    )


    # ========================================================
    # ANIMALS / VEHICLES / NATURE
    # ========================================================

    st.markdown(
        "### 🐶 Animals / 🚗 Vehicles / 🌳 Nature"
    )

    st.write(
        "a cute kitten • "
        "a dog • "
        "cars and vehicles • "
        "nature landscape • "
        "trees and greenery"
    )


    # ========================================================
    # DOCUMENTS
    # ========================================================

    st.markdown(
        "### 📄 Documents"
    )

    st.write(
        "annual report • "
        "data analytics • "
        "machine learning • "
        "brochure"
    )