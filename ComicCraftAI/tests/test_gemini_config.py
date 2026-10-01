import unittest
from unittest.mock import MagicMock, patch

from app.ai.gemini_flash import _candidate_models, generate_outline
from app.config import Settings
from app.exporters import save_pdf


class GeminiModelConfigTest(unittest.TestCase):
    def test_default_flash_model_uses_supported_name(self):
        self.assertEqual(Settings().gemini_flash_model, "gemini-3.8-flash")

    def test_default_comic_panels_uses_six(self):
        self.assertEqual(Settings().comic_panels, 6)

    def test_candidate_models_include_fallbacks(self):
        settings = Settings(gemini_flash_model="gemini-2.5-flash")
        models = _candidate_models(settings)

        self.assertEqual(models[0], "gemini-2.5-flash")
        self.assertIn("gemini-3.8-flash", models)
        self.assertIn("gemini-2.0-flash", models)

    @patch("app.ai.gemini_flash.get_settings")
    def test_generate_outline_uses_demo_fallback_on_high_demand(self, mock_get_settings):
        settings = Settings(gemini_api_key="test-key")
        mock_get_settings.return_value = settings

        client = MagicMock()
        client.models.generate_content.side_effect = RuntimeError(
            "503 UNAVAILABLE. This model is currently experiencing high demand."
        )

        mock_genai = MagicMock()
        mock_genai.Client.return_value = client

        with patch("app.ai.gemini_flash.genai", mock_genai), \
             patch("app.ai.gemini_flash.types", MagicMock(GenerateContentConfig=MagicMock())):
            result = generate_outline(
                "A brave fox in a moonlit forest",
                "Luna",
                "moonlit forest",
                "dramatic",
                "comic book",
            )

        self.assertEqual(len(result), settings.comic_panels)
        self.assertEqual(result[0]["panel_number"], 1)

    def test_save_pdf_handles_demo_layout(self):
        layout = [{
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description": "Luna enters the forest.",
            "image_url": "/static/panels/demo.png",
        }]

        result = save_pdf(layout)

        self.assertTrue(result.startswith("/download/"))


if __name__ == "__main__":
    unittest.main()
