import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.search.search_engine import semantic_search


QUERIES = [
    "a cricket match",
    "cricket stadium",
    "spectators watching a sports event",
    "a person taking a photograph at a cricket match",
    "professional sports event",
    "people in a stadium",
    "a cute kitten",
    "a dog",
    "AI and machine learning projects",
    "water delivery marketplace"
]


def main():

    print()
    print("=" * 60)
    print("SEMANTIC SEARCH EVALUATION")
    print("=" * 60)

    for query in QUERIES:

        print()
        print("=" * 60)
        print(f"QUERY: {query}")
        print("=" * 60)

        results = semantic_search(
            query,
            top_k=3
        )

        for rank, result in enumerate(
            results,
            start=1
        ):

            print()
            print(f"{rank}. {result['filename']}")
            print(f"   Score: {result['score']:.4f}")
            print(f"   Type: {result['file_type']}")


if __name__ == "__main__":
    main()
