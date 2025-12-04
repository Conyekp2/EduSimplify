import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# Serve /static (logo, avatar, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main page
@app.get("/")
async def read_index():
    return FileResponse("index.html")


class SimplifyRequest(BaseModel):
    text: str
    target_level: str | None = None


@app.post("/simplify")
async def simplify_text(request: SimplifyRequest):
    target = request.target_level if request.target_level else "A2 (Elementary)"

    system_prompt = (
        "You are a strict French language expert. "
        "You must Output ONLY valid JSON."
    )

    user_prompt = f"""
    Task:
    1. Analyze the CEFR level of the input text (A1, A2, B1, B2, C1, or C2).
    2. Simplify the text to the target level: {target}.

    Input Text:
    "{request.text}"

    Response Format (JSON only):
    {{
        "detected_level": "Level detected (e.g. B2)",
        "target_level": "{target}",
        "simplified_text": "The simplified French text...",
        "cefr_explanation": "Brief reason why the original is this level.",
        "level_explanation": "French explanation of the original CEFR level.",
        "simplification_strategy": "French explanation of how the text was simplified."
    }}
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": False,
                "format": "json",
            },
            timeout=60,
        )

        result = response.json()
        ai_data = json.loads(result["response"])
        return ai_data

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
