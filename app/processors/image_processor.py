import base64
from pathlib import Path

import requests


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434"

VISION_MODEL = "llava:7b"


# ============================================================
# IMAGE → BASE64
# ============================================================

def image_to_base64(image_path: str) -> str:
    """
    Convert an image file into a base64 encoded string.
    """

    with open(image_path, "rb") as file:

        return base64.b64encode(
            file.read()
        ).decode("utf-8")


# ============================================================
# IMAGE DESCRIPTION
# ============================================================

def describe_image(image_path: str) -> str:
    """
    Generate a search-oriented AI description of an image
    using LLaVA.

    The description is designed for semantic search rather
    than just general image captioning.
    """

    image_path = str(
        Path(image_path).resolve()
    )

    image_base64 = image_to_base64(
        image_path
    )


    # ========================================================
    # SEARCH-ORIENTED PROMPT
    # ========================================================

    prompt = """
Analyze this image for an AI-powered Digital Asset Management
system.

Create a concise but information-rich description that is useful
for natural-language semantic search.

Identify the following when visible:

1. MAIN SUBJECTS
   - people
   - animals
   - vehicles
   - buildings
   - machines
   - objects
   - devices

2. PEOPLE AND THEIR ROLE
   Examples:
   - construction worker
   - factory worker
   - engineer
   - technician
   - athlete
   - customer
   - office worker
   - photographer

3. ACTIONS / ACTIVITIES
   Examples:
   - construction
   - building
   - repairing
   - assembling
   - manufacturing
   - playing sports
   - taking photographs
   - using a computer
   - driving

4. ENVIRONMENT / LOCATION
   Examples:
   - construction site
   - factory
   - workshop
   - office
   - stadium
   - road
   - laboratory
   - home
   - outdoor area

5. IMPORTANT OBJECTS
   Mention visually important objects such as:
   - construction equipment
   - helmets
   - machinery
   - tools
   - computers
   - electronic components
   - vehicles
   - sports equipment

6. VISUAL CONTEXT
   Describe what is happening and how the subjects,
   objects and environment relate to each other.

7. SEARCHABLE CONCEPTS
   End with a short list of concrete keywords/concepts
   that someone might use to search for this image.

IMPORTANT RULES:

- Only describe things that are actually visible.
- Do not invent details.
- Do not assume an environment that cannot be seen.
- Distinguish between construction, factory/manufacturing,
  office, technology, sports, nature, etc.
- Use concrete searchable terms.
- Prefer specific concepts over vague words such as
  "people", "activity", or "place".
- Keep the total response reasonably concise.

Return the result in this format:

Subjects:
...

People/Roles:
...

Activities:
...

Environment:
...

Objects:
...

Visual Context:
...

Search Concepts:
...
"""


    # ========================================================
    # OLLAMA REQUEST
    # ========================================================

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",

        json={
            "model": VISION_MODEL,

            "prompt": prompt,

            "images": [
                image_base64
            ],

            "stream": False
        },

        timeout=180
    )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    response.raise_for_status()


    # ========================================================
    # RESPONSE
    # ========================================================

    result = response.json()

    description = result.get(
        "response",
        ""
    ).strip()


    if not description:

        raise ValueError(
            "LLaVA returned an empty image description."
        )


    return description