from pydantic import BaseModel, ConfigDict, Field


class PromptRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    story_prompt: str = Field(..., min_length=3, max_length=3000)
    character_name: str = Field(..., min_length=1, max_length=80)
    setting: str = Field(..., min_length=1, max_length=120)
    tone: str = Field(..., min_length=1, max_length=40)
    art_style: str = Field(..., min_length=1, max_length=40)


class PanelOutline(BaseModel):
    model_config = ConfigDict(extra="ignore")

    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
