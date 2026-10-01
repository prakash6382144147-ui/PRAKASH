from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_gemini_model(model_name: str | None) -> str:
    if not model_name:
        return "gemini-3.8-flash"

    cleaned = model_name.strip().removeprefix("models/")
    deprecated = {
        "gemini-2.5-flash": "gemini-3.8-flash",
        "gemini-2.5-pro": "gemini-3.8-flash",
    }
    return deprecated.get(cleaned, cleaned)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    hf_api_key: str = ""
    image_provider: str = "demo"
    comic_panels: int = 5
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-3.8-flash"


def get_settings() -> Settings:
    return Settings()
