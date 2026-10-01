import json
import re

from app.config import get_settings, normalize_gemini_model
from app.schemas import PanelOutline


try:

    from google import genai
    from google.genai import types

except ImportError:

    genai = None
    types = None


def _extract_json(text: str):

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    return json.loads(text)


def _should_fallback_to_demo(exc: Exception) -> bool:
    text = str(exc).lower()
    triggers = (
        "unavailable",
        "rate limit",
        "429",
        "503",
        "timeout",
        "temporarily",
        "resource exhausted",
        "quota",
        "not found",
        "overloaded",
        "capacity",
        "busy",
    )
    return any(trigger in text for trigger in triggers)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):

    settings = get_settings()

    # --------------------------------
    # Demo mode
    # --------------------------------

    if not settings.gemini_api_key:

        return _demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

    # --------------------------------
    # Check package
    # --------------------------------

    if genai is None:

        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install -r requirements.txt"
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
Create exactly {settings.comic_panels} panels
for a coherent comic story.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

Each array item must contain:

panel_number
title
scene_description
image_prompt

Rules:

1. Create exactly {settings.comic_panels} panels.
2. Keep the main character visually consistent.
3. Maintain story continuity.
4. Image prompts must describe visual content only.
5. Do not include speech bubbles.
6. Do not include text inside the generated image.
7. Do not include logos.
8. Do not include watermarks.
9. Do not use copyrighted character names.
"""

    try:
        response = client.models.generate_content(

            model=normalize_gemini_model(settings.gemini_flash_model),

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.8,

                response_mime_type="application/json",

            ),
        )

        data = _extract_json(response.text)

    except Exception as exc:
        if _should_fallback_to_demo(exc):
            return _demo_outline(
                story_prompt,
                character_name,
                setting,
                tone,
                art_style,
            )
        raise

    if not isinstance(data, list):

        raise ValueError(
            "Gemini returned an invalid comic outline."
        )

    if len(data) != settings.comic_panels:

        raise ValueError(
            "Gemini did not return the required "
            "number of panels."
        )

    return [
        PanelOutline.model_validate(item).model_dump()
        for item in data
    ]


def _demo_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    beats = [

        (
            "The Beginning",

            f"{character_name} arrives in {setting}, "
            "ready to face an unexpected mystery."
        ),

        (
            "A Strange Sign",

            f"A mysterious clue appears, "
            f"changing {character_name}'s plan."
        ),

        (
            "The Challenge",

            f"{character_name} confronts the central "
            f"obstacle in this {tone} story."
        ),

        (
            "The Turning Point",

            f"A clever discovery gives "
            f"{character_name} a new path forward."
        ),

        (
            "A New Dawn",

            f"{character_name} reaches a satisfying "
            "conclusion and looks toward the future."
        ),

    ]

    result = []

    for index, (title, description) in enumerate(beats):

        result.append({

            "panel_number": index + 1,

            "title": title,

            "scene_description": (
                description +
                f" Story idea: {story_prompt}"
            ),

            "image_prompt": (
                f"{art_style} comic illustration, "
                f"panel {index + 1}, "
                f"{description}, "
                f"recurring hero named {character_name}, "
                f"setting: {setting}, "
                "cinematic composition, "
                "expressive face, "
                "detailed background, "
                "no text, no watermark"
            ),

        })

    return result