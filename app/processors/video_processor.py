import base64
from pathlib import Path

import cv2
import requests


OLLAMA_URL = "http://localhost:11434"
VISION_MODEL = "llava:7b"


def get_video_info(video_path: str):
    """
    Get basic video metadata.
    """

    video_path = Path(video_path)

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

    width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    duration = (
        frame_count / fps
        if fps > 0
        else 0
    )

    capture.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration": duration
    }


def calculate_sample_count(duration: float) -> int:
    """
    Decide how many representative frames to sample.

    The goal is to keep LLaVA inference manageable
    while still capturing useful video content.
    """

    if duration <= 10:
        return 3

    elif duration <= 30:
        return 5

    elif duration <= 60:
        return 8

    else:
        return 10


def sample_video_frames(
    video_path: str,
    max_frames: int | None = None
):
    """
    Sample representative frames across the entire video.

    Instead of processing every N seconds, this method
    distributes a limited number of frames across the
    video duration.

    Returns:
        List of dictionaries containing:
        - timestamp
        - frame
    """

    video_path = Path(video_path)

    info = get_video_info(str(video_path))

    duration = info["duration"]

    if duration <= 0:
        raise RuntimeError(
            "Could not determine video duration."
        )

    if max_frames is None:
        max_frames = calculate_sample_count(
            duration
        )

    # Do not request more frames than necessary.
    max_frames = max(
        1,
        min(max_frames, 10)
    )

    capture = cv2.VideoCapture(
        str(video_path)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    frames = []

    # Avoid sampling exactly at the beginning/end.
    if max_frames == 1:
        timestamps = [duration / 2]

    else:
        start = min(0.5, duration * 0.05)
        end = max(
            start,
            duration - min(0.5, duration * 0.05)
        )

        step = (
            end - start
        ) / (max_frames - 1)

        timestamps = [
            start + (step * i)
            for i in range(max_frames)
        ]

    for timestamp in timestamps:

        capture.set(
            cv2.CAP_PROP_POS_MSEC,
            timestamp * 1000
        )

        success, frame = capture.read()

        if not success:
            continue

        frames.append(
            {
                "timestamp": float(timestamp),
                "frame": frame
            }
        )

    capture.release()

    return frames


def describe_video_frame(frame) -> str:
    """
    Send a video frame to LLaVA and generate
    a searchable natural-language description.
    """

    # Keep image size reasonable for local inference.
    frame = cv2.resize(
        frame,
        (960, 540)
    )

    success, encoded_image = cv2.imencode(
        ".jpg",
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            85
        ]
    )

    if not success:
        raise RuntimeError(
            "Could not encode video frame."
        )

    image_base64 = base64.b64encode(
        encoded_image.tobytes()
    ).decode("utf-8")

    prompt = """
Analyze this video frame for an AI-powered
Digital Asset Management system.

Create a concise description useful for
natural-language semantic search.

Identify visible:

- People and their roles
- Animals
- Vehicles
- Buildings
- Machines and equipment
- Objects
- Activities and actions
- Sports
- Construction activity
- Industrial or factory activity
- Environment/location
- Important visible text
- Other important visual details

Focus only on what is actually visible.

Do not invent details.

Use concrete searchable terms instead of
generic descriptions.

Examples of useful concepts include:
construction worker, construction site,
factory worker, manufacturing, cricket match,
football game, vehicle, road, office,
computer, machinery, residential building,
living room, outdoor activity.

Keep the response concise.
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    description = (
        result.get("response", "")
        .strip()
    )

    if not description:
        raise RuntimeError(
            "LLaVA returned an empty description."
        )

    return description


if __name__ == "__main__":

    video_path = (
        "dataset/videos/sports/video 1 cric.mp4"
    )

    print()
    print("=" * 60)
    print("VIDEO AI UNDERSTANDING TEST")
    print("=" * 60)

    info = get_video_info(video_path)

    print()
    print("Video information:")
    print(
        f"  FPS       : {info['fps']:.2f}"
    )
    print(
        f"  Frames    : {int(info['frame_count'])}"
    )
    print(
        f"  Resolution: "
        f"{info['width']} x {info['height']}"
    )
    print(
        f"  Duration  : "
        f"{info['duration']:.2f} seconds"
    )

    sample_count = calculate_sample_count(
        info["duration"]
    )

    print()
    print(
        f"Sampling {sample_count} representative frames..."
    )

    frames = sample_video_frames(
        video_path,
        max_frames=sample_count
    )

    print(
        f"Frames sampled: {len(frames)}"
    )

    for index, item in enumerate(
        frames,
        start=1
    ):

        timestamp = item["timestamp"]
        frame = item["frame"]

        print()
        print(
            f"[FRAME {index}] "
            f"{timestamp:.2f} seconds"
        )

        description = describe_video_frame(
            frame
        )

        print(
            f"Description: {description}"
        )

    print()
    print("=" * 60)
    print("VIDEO AI UNDERSTANDING COMPLETED")
    print("=" * 60)