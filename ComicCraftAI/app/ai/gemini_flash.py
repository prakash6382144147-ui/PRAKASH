import json
import re

from app.config import get_settings
from app.schemas import PanelOutline


try:

    from google import genai
    from google.genai import types

except ImportError:

    genai = None
    types = None


def _candidate_models(settings):
    preferred = (settings.gemini_flash_model or "").strip()
    fallback = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ]

    models = []

    for name in ([preferred] if preferred else []) + fallback:
        if name and name not in models:
            models.append(name)

    return models


def _should_use_demo_fallback(exc):
    message = str(exc).upper()
    markers = (
        "503",
        "429",
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "RATE_LIMIT",
        "HIGH DEMAND",
        "TOO_MANY_REQUESTS",
    )
    return any(marker in message for marker in markers)


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

    last_error = None

    for model_name in _candidate_models(settings):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    response_mime_type="application/json",
                ),
            )

            data = _extract_json(response.text)

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

        except Exception as exc:
            if not _should_use_demo_fallback(exc):
                if "404" not in str(exc).upper() and "NOT_FOUND" not in str(exc).upper():
                    raise

            last_error = exc

    if last_error is not None:
        return _demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
            settings.comic_panels,
        )

    raise RuntimeError(
        "Gemini model lookup failed for all configured model names. "
        f"Last error: {last_error}"
    )


def _demo_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style,
    comic_panels=5
):

    beats = [

        (
            "The Beginning",

            f"{character_name} arrives in {setting}, "
            "ready to face an unexpected mystery."
        ),

        (
            "The Warning",

            f"Talking trees and magical creatures reveal "
            f"that a dark spell is spreading across {setting}."
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

    selected_beats = beats[:comic_panels]

    if len(selected_beats) < comic_panels:
        selected_beats = beats * ((comic_panels // len(beats)) + 1)
        selected_beats = selected_beats[:comic_panels]

    result = []

    for index, (title, description) in enumerate(selected_beats):

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