def build_comic_layout(story, image_paths):
    layout = []

    for index, panel in enumerate(story):
        if isinstance(panel, dict):
            item = {
                "panel_number": panel.get("panel_number", index + 1),
                "title": panel.get("title", f"Panel {index + 1}"),
                "scene_description": panel.get("scene_description", ""),
                "image_prompt": panel.get("image_prompt", ""),
                "image_url": image_paths[index] if index < len(image_paths) else "",
            }
        else:
            item = {
                "panel_number": index + 1,
                "title": f"Panel {index + 1}",
                "scene_description": str(panel),
                "image_prompt": "",
                "image_url": image_paths[index] if index < len(image_paths) else "",
            }

        layout.append(item)

    return layout
