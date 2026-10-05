import sys
from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_step(step_name, script_path):

    print()
    print("=" * 60)
    print(step_name)
    print("=" * 60)

    command = [
        sys.executable,
        str(PROJECT_ROOT / script_path)
    ]

    try:

        result = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if output:
            print(output)

        if error:
            print(error)

        return {
            "step": step_name,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": output,
            "error": error
        }

    except Exception as exc:

        return {
            "step": step_name,
            "success": False,
            "returncode": -1,
            "output": "",
            "error": str(exc)
        }


def run_reindex_pipeline():

    steps = [

        (
            "1. Incremental Indexing",
            "app/ingestion/indexer.py"
        ),

        (
            "2. Image AI Indexing",
            "app/processors/image_indexer.py"
        ),

        (
            "3. PDF AI Indexing",
            "app/processors/pdf_indexer.py"
        ),

        (
            "4. Video AI Indexing",
            "app/processors/video_indexer.py"
        ),

        (
            "5. FAISS Rebuild",
            "app/search/rebuild_index.py"
        )
    ]

    results = []

    for step_name, script_path in steps:

        result = run_step(
            step_name,
            script_path
        )

        results.append(result)

        if not result["success"]:

            print()
            print(
                f"[FAILED] {step_name}"
            )

            break

    return results


if __name__ == "__main__":

    results = run_reindex_pipeline()

    print()
    print("=" * 60)
    print("REINDEX SUMMARY")
    print("=" * 60)

    for result in results:

        status = (
            "SUCCESS"
            if result["success"]
            else "FAILED"
        )

        print(
            f"{status}: {result['step']}"
        )

    print()
