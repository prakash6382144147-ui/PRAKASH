from app.config import get_settings


def generate_story(outline, character_name: str, tone: str, art_style: str):
    settings = get_settings()

    if not outline:
        return []

    if not settings.gemini_api_key:
        return [
            {
                "panel_number": item.get("panel_number", index + 1),
                "title": item.get("title", f"Panel {index + 1}"),
                "scene_description": item.get(
                    "scene_description",
                    f"{character_name} moves through a {tone} scene inspired by {art_style} artwork.",
                ),
                "image_prompt": item.get(
                    "image_prompt",
                    f"{art_style}, {tone}, cinematic comic scene featuring {character_name}",
                ),
            }
            for index, item in enumerate(outline)
        ]

    story = []
    for item in outline:
        narration = item.get("scene_description", "")
        story.append(
            {
                "panel_number": item.get("panel_number"),
                "title": item.get("title", "Untitled Panel"),
                "scene_description": narration,
                "image_prompt": item.get("image_prompt", narration),
            }
        )

    return story
