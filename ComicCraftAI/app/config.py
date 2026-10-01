from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-3.8-flash"
    hf_api_key: str = ""
    hf_image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    image_provider: str = "auto"
    use_local_diffusers: bool = False
    local_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    comic_panels: int = 6
    image_width: int = 768
    image_height: int = 768

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
