from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .simplify import simplify_text

app = FastAPI(title="EduSimplify")

# Dossier des fichiers statiques (index.html, CSS, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class SimplifyRequest(BaseModel):
    text: str
    mode: str = "standard"      # "light" | "standard" | "strong"
    strategy: str = "auto"      # "auto" | "target"
    target: Optional[str] = None   # "A1"…"C1" si strategy="target"
    engine: str = "rules"       # "rules" | "llm"


@app.get("/", response_class=HTMLResponse)
def root():
    """
    Sert l'interface web si index.html existe,
    sinon un simple message JSON.
    """
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")

    # Fallback si pas d'index
    return HTMLResponse(
        content='{"message": "EduSimplify API is running. Open /static/index.html for the UI."}',
        media_type="application/json",
    )


@app.post("/simplify")
def simplify(req: SimplifyRequest):
    """
    Endpoint principal :
    - applique la pipeline de simplification (Rules ou LLM)
    - renvoie les infos attendues par le frontend
    """
    result = simplify_text(
        text=req.text,
        mode=req.mode,
        strategy=req.strategy,
        target=req.target,
        engine=req.engine,
    )
    return result