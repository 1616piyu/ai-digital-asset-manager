import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from app.search.search_engine import semantic_search


# ---------------------------------------------------------
# Evaluation queries
# ---------------------------------------------------------

TEST_QUERIES = [

    {
        "query": "a cricket match",
        "expected": "video 1 cric.mp4"
    },

    {
        "query": "cricket stadium",
        "expected": "video 1 cric.mp4"
    },

    {
        "query": "spectators watching a sports event",
        "expected": "video 1 cric.mp4"
    },

    {
        "query": "people in a stadium",
        "expected": "video 1 cric.mp4"
    },

    {
        "query": "professional sports event",
        "expected": "video 1 cric.mp4"
    },

    {
        "query": "a cute kitten",
        "expected": "cat 1.jpg"
    },

    {
        "query": "a cat",
        "expected": "cat 1.jpg"
    },

    {
        "query": "a dog",
        "expected": "dog 1.jpg"
    },

    {
        "query": "AI and machine learning projects",
        "expected": (
            "Piyush_Pratap_Singh_Dream11_AI_Projects_Portfolio.pdf"
        )
    },

    {
        "query": "water delivery marketplace",
        "expected": (
            "Piyush_Pratap_Singh_Dream11_AI_Projects_Portfolio.pdf"
        )
    }
]


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate():

    print()
    print("=" * 70)
    print("SEMANTIC SEARCH EVALUATION")
    print("=" * 70)

    total = len(TEST_QUERIES)

    top_1_correct = 0
    top_3_correct = 0

    for number, test in enumerate(
        TEST_QUERIES,
        start=1
    ):

        query = test["query"]
        expected = test["expected"]

        print()
        print("-" * 70)
        print(f"TEST {number}/{total}")
        print(f"Query    : {query}")
        print(f"Expected : {expected}")

        try:

            results = semantic_search(
                query,
                top_k=3
            )

        except Exception as error:

            print(f"ERROR: {error}")
            continue

        filenames = [
            result["filename"]
            for result in results
        ]

        # -------------------------------------------------
        # Top 1
        # -------------------------------------------------

        if (
            len(filenames) > 0
            and filenames[0] == expected
        ):

            top_1_correct += 1

            print("Top-1   : PASS")

        else:

            print("Top-1   : FAIL")


        # -------------------------------------------------
        # Top 3
        # -------------------------------------------------

        if expected in filenames:

            top_3_correct += 1

            print("Top-3   : PASS")

        else:

            print("Top-3   : FAIL")


        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        print()
        print("Results:")

        for rank, result in enumerate(
            results,
            start=1
        ):

            print(
                f"{rank}. "
                f"{result['filename']} "
                f""
                f"(score={result['score']:.4f})"
            )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    top_1_accuracy = (
        top_1_correct / total * 100
    )

    top_3_accuracy = (
        top_3_correct / total * 100
    )


    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Total queries     : {total}"
    )

    print(
        f"Top-1 correct     : {top_1_correct}/{total}"
    )

    print(
        f"Top-1 accuracy    : {top_1_accuracy:.1f}%"
    )

    print(
        f"Top-3 correct     : {top_3_correct}/{total}"
    )

    print(
        f"Top-3 accuracy    : {top_3_accuracy:.1f}%"
    )

    print()


if __name__ == "__main__":
    evaluate()