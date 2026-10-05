import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.database.database import (
    initialize_database,
    get_connection
)

from app.processors.video_processor import (
    sample_video_frames,
    describe_video_frame,
    get_video_info,
    calculate_sample_count
)

from app.embeddings.ollama_embeddings import (
    create_embedding
)

from app.search.vector_store import (
    load_index,
    add_vector,
    save_index
)


def process_videos():

    print()
    print("=" * 60)
    print("VIDEO AI INDEXER")
    print("=" * 60)
    print()

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # FIND VIDEOS THAT STILL NEED PROCESSING
    # --------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            filename,
            path
        FROM assets
        WHERE
            file_type = 'video'
            AND (
                embedding_status IS NULL
                OR embedding_status != 'completed'
            )
        ORDER BY id
        """
    )

    assets = cursor.fetchall()

    if not assets:

        print("No videos need processing.")
        connection.close()
        return

    print(
        f"Videos to process: {len(assets)}"
    )
    print()

    # --------------------------------------------------
    # LOAD EXISTING FAISS INDEX
    # --------------------------------------------------

    index = load_index()

    processed_videos = 0
    failed_videos = 0

    total_frames = 0
    successful_frames = 0
    failed_frames = 0

    # --------------------------------------------------
    # PROCESS VIDEOS
    # --------------------------------------------------

    for video_number, asset in enumerate(
        assets,
        start=1
    ):

        asset_id = asset["id"]
        filename = asset["filename"]
        video_path = asset["path"]

        print("=" * 60)
        print(
            f"[VIDEO {video_number}/{len(assets)}]"
        )
        print(
            f"{filename}"
        )
        print("=" * 60)

        try:

            # --------------------------------------------------
            # GET VIDEO INFORMATION
            # --------------------------------------------------

            info = get_video_info(
                video_path
            )

            duration = info["duration"]

            sample_count = (
                calculate_sample_count(
                    duration
                )
            )

            print(
                f"Duration       : "
                f"{duration:.2f} sec"
            )

            print(
                f"Sample frames  : "
                f"{sample_count}"
            )

            # --------------------------------------------------
            # SAMPLE REPRESENTATIVE FRAMES
            # --------------------------------------------------

            frames = sample_video_frames(
                video_path,
                max_frames=sample_count
            )

            print(
                f"Frames extracted: "
                f"{len(frames)}"
            )

            total_frames += len(frames)

            if not frames:
                raise RuntimeError(
                    "No frames could be extracted."
                )

            video_descriptions = []

            # --------------------------------------------------
            # PROCESS FRAMES
            # --------------------------------------------------

            for frame_number, frame_data in enumerate(
                frames,
                start=1
            ):

                timestamp = frame_data[
                    "timestamp"
                ]

                frame = frame_data[
                    "frame"
                ]

                print()
                print(
                    f"  [FRAME "
                    f"{frame_number}/"
                    f"{len(frames)}] "
                    f"{timestamp:.2f}s"
                )

                try:

                    # ------------------------------------------
                    # LLaVA
                    # ------------------------------------------

                    description = (
                        describe_video_frame(
                            frame
                        )
                    )

                    print(
                        "    LLaVA: completed"
                    )

                    # ------------------------------------------
                    # EMBEDDING
                    # ------------------------------------------

                    embedding = (
                        create_embedding(
                            description
                        )
                    )

                    print(
                        "    Embedding: completed"
                    )

                    # ------------------------------------------
                    # ADD VECTOR
                    # ------------------------------------------

                    vector_id = index.ntotal

                    add_vector(
                        index,
                        embedding
                    )

                    # ------------------------------------------
                    # STORE VECTOR MAPPING
                    # ------------------------------------------

                    cursor.execute(
                        """
                        INSERT INTO asset_vectors (
                            asset_id,
                            vector_id,
                            content_type,
                            content_text,
                            timestamp_seconds
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            asset_id,
                            vector_id,
                            "video_frame",
                            description,
                            timestamp
                        )
                    )

                    # ------------------------------------------
                    # CHECKPOINT FRAME
                    # ------------------------------------------

                    connection.commit()
                    save_index(index)

                    successful_frames += 1

                    video_descriptions.append(
                        description
                    )

                    print(
                        f"    Vector ID: "
                        f"{vector_id}"
                    )

                    print(
                        "    Checkpoint saved ✓"
                    )

                except Exception as frame_error:

                    failed_frames += 1

                    print(
                        f"    FRAME ERROR: "
                        f"{frame_error}"
                    )

                    # Continue with next frame.
                    continue

            # --------------------------------------------------
            # CHECK SUCCESS
            # --------------------------------------------------

            if not video_descriptions:

                raise RuntimeError(
                    "All video frames failed."
                )

            # --------------------------------------------------
            # COMBINE VIDEO DESCRIPTIONS
            # --------------------------------------------------

            combined_description = (
                "Video containing the following "
                "observed scenes:\n\n"
                + "\n".join(
                    video_descriptions
                )
            )

            # --------------------------------------------------
            # UPDATE VIDEO STATUS
            # --------------------------------------------------

            cursor.execute(
                """
                UPDATE assets
                SET
                    ai_description = ?,
                    embedding_status = ?,
                    status = ?,
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    combined_description,
                    "completed",
                    "completed",
                    asset_id
                )
            )

            connection.commit()
            save_index(index)

            processed_videos += 1

            print()
            print(
                "  VIDEO STATUS: COMPLETED ✓"
            )

        except Exception as video_error:

            failed_videos += 1

            cursor.execute(
                """
                UPDATE assets
                SET
                    embedding_status = ?,
                    status = ?,
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    "failed",
                    "failed",
                    str(video_error),
                    asset_id
                )
            )

            connection.commit()
            save_index(index)

            print()
            print(
                f"  VIDEO ERROR: "
                f"{video_error}"
            )

            print(
                "  Other videos will continue."
            )

        print()

    # --------------------------------------------------
    # FINAL SAVE
    # --------------------------------------------------

    save_index(index)
    connection.commit()

    connection.close()

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("=" * 60)
    print("VIDEO INDEXING SUMMARY")
    print("=" * 60)

    print(
        f"Videos found       : "
        f"{len(assets)}"
    )

    print(
        f"Videos processed   : "
        f"{processed_videos}"
    )

    print(
        f"Videos failed      : "
        f"{failed_videos}"
    )

    print(
        f"Total frames       : "
        f"{total_frames}"
    )

    print(
        f"Successful frames  : "
        f"{successful_frames}"
    )

    print(
        f"Failed frames      : "
        f"{failed_frames}"
    )

    print(
        f"FAISS total vectors: "
        f"{index.ntotal}"
    )

    print()
    print(
        "Video indexing completed."
    )


if __name__ == "__main__":
    process_videos()