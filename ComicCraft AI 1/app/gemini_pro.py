def generate_story(outline, character_name: str, tone: str, art_style: str):
    """Create a simple story payload from the outline in demo mode."""
    story = []

    for panel in outline:
        scene = panel.get("scene_description", "")
        story.append(
            {
                "panel_number": panel.get("panel_number"),
                "title": panel.get("title", f"Panel {panel.get('panel_number', 1)}"),
                "scene_description": scene,
                "image_prompt": (
                    f"{art_style} comic illustration, {character_name}, "
                    f"{tone} mood, {scene}, cinematic composition, no text, no watermark"
                ),
            }
        )

    return story
