from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from app.config import get_settings

from app.exporters import save_pdf

from app.gemini_flash import (
    generate_outline
)

from app.gemini_pro import (
    generate_story
)

from app.image_generator import (
    generate_image
)

from app.layout_builder import (
    build_comic_layout
)

from app.schemas import (
    PromptRequest
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)


templates = Jinja2Templates(

    directory=str(
        BASE_DIR / "templates"
    )

)


router = APIRouter()


def create_comic(
    payload: PromptRequest
):

    # --------------------------------
    # STEP 1
    # Generate outline
    # --------------------------------

    outline = generate_outline(

        payload.story_prompt,

        payload.character_name,

        payload.setting,

        payload.tone,

        payload.art_style,

    )

    # --------------------------------
    # STEP 2
    # Generate story
    # --------------------------------

    story = generate_story(

        outline,

        payload.character_name,

        payload.tone,

        payload.art_style,

    )

    # --------------------------------
    # STEP 3
    # Generate images
    # --------------------------------

    image_paths = []

    for panel in story:

        image = generate_image(

            panel["image_prompt"],

            panel["panel_number"]

        )

        image_paths.append(image)

    # --------------------------------
    # STEP 4
    # Build layout
    # --------------------------------

    layout = build_comic_layout(

        story,

        image_paths

    )

    # --------------------------------
    # STEP 5
    # Export PDF
    # --------------------------------

    pdf_url = save_pdf(
        layout
    )

    return layout, pdf_url


# ====================================
# HOME
# ====================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "settings":
                get_settings()
        }

    )


# ====================================
# HTML GENERATION
# ====================================

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)

):

    try:

        payload = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style

        )

        layout, pdf_url = create_comic(
            payload
        )

        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={

                "layout": layout,

                "pdf_url": pdf_url

            }

        )

    except Exception as exc:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "error": str(exc),

                "settings":
                    get_settings()

            },

            status_code=500

        )


# ====================================
# JSON API
# ====================================

@router.post(
    "/generate-comic/json"
)
async def generate_json(
    payload: PromptRequest
):

    try:

        layout, pdf_url = create_comic(
            payload
        )

        return {

            "success": True,

            "panels": layout,

            "pdf_url": pdf_url

        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)

        ) from exc


# ====================================
# TEST IMAGE
# ====================================

@router.post(
    "/test-image"
)
async def test_image(

    prompt: str = Form(...)

):

    try:

        image_url = generate_image(

            prompt,

            0

        )

        return {

            "success": True,

            "image_url": image_url

        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)

        ) from exc


# ====================================
# DOWNLOAD PDF
# ====================================

@router.get(
    "/download/{filename}"
)
async def download(
    filename: str
):

    safe_name = Path(
        filename
    ).name

    file_path = (

        BASE_DIR /

        "static" /

        "exports" /

        safe_name

    )

    if not file_path.exists():

        raise HTTPException(

            status_code=404,

            detail="PDF not found."

        )

    return FileResponse(

        path=file_path,

        media_type="application/pdf",

        filename=safe_name

    )


# ====================================
# EXPORT SUCCESS
# ====================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    filename: str | None = None

):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={
            "filename": filename
        }

    )


# ====================================
# HEALTH
# ====================================

@router.get(
    "/health"
)
async def health():

    settings = get_settings()

    return {

        "status": "ok",

        "gemini_configured":
            bool(
                settings.gemini_api_key
            ),

        "huggingface_configured":
            bool(
                settings.hf_api_key
            ),

        "image_provider":
            settings.image_provider

    }