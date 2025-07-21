from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services import translate_text

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Bengali": "bn",
    "Kannada": "kn",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Telugu": "te",
    "Gujarati": "gu",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Urdu": "ur",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN"
}

# For also enabling the JSON schema for POST requests
class TranslationRequest(BaseModel):
    text: str
    language: str


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "langs": SUPPORTED_LANGUAGES
    })


@app.post("/translate")
async def translate(
    request: Request,
    text: str = Form(None),
    language: str = Form(None),
    json_data: TranslationRequest = Body(None)
):
    try:
        
        if json_data:
            text_lines = [line.strip() for line in json_data.text.splitlines() if line.strip()]
            if not text_lines:
                return JSONResponse(content={"error": "Text cannot be empty."}, status_code=400)
            if sum(len(line) for line in text_lines) > 1000:
                return JSONResponse(content={"error": "Total input length must be under 1000 characters."}, status_code=400)

            translated_lines = [translate_text(line, json_data.language) for line in text_lines]
            return JSONResponse(content={"translated": translated_lines})

        
        if not text or not language:
            error = "Text and language are required."
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": error,
                "langs": SUPPORTED_LANGUAGES
            })

        text_lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not text_lines:
            error = "Text cannot be empty."
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": error,
                "langs": SUPPORTED_LANGUAGES
            })

        if sum(len(line) for line in text_lines) > 1000:
            error = "Total input length must be under 1000 characters."
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": error,
                "langs": SUPPORTED_LANGUAGES
            })

        translated_lines = [translate_text(line, language) for line in text_lines]
        translated_text = "\n".join(translated_lines)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "original": text,
            "translated": translated_text,
            "language": language,
            "langs": SUPPORTED_LANGUAGES
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
class TranslationRequest(BaseModel):
    text: str
    language: str

@app.post("/api/translate")
async def translate_api(request: TranslationRequest):
    translated = translate_text(request.text, request.language)
    return JSONResponse(content={"translated_text": translated})


@app.get("/health", response_class=HTMLResponse)
async def health_check(request: Request):
    return templates.TemplateResponse("health.html", {
        "request": request,
        "status": "Translation service is up and you are good to go✨"
    })
