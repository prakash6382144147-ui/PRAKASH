def build_comic_layout(story, image_paths):
    """Turn story panels and image URLs into a list of preview rows."""
    layout = []

    for index, panel in enumerate(story):
        image_url = image_paths[index] if index < len(image_paths) else ""
        layout.append(
            {
                "panel_number": panel.get("panel_number", index + 1),
                "title": panel.get("title", f"Panel {index + 1}"),
                "scene_description": panel.get("scene_description", ""),
                "image_url": image_url,
            }
        )

    return layout
