from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .simplify import simplify_text
from .cefr import analyze_text

app = FastAPI(title="EduSimplify")

# Dossier des fichiers statiques (index.html, CSS, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class SimplifyRequest(BaseModel):
    text: str
    mode: str = "standard"      # "light" | "standard" | "strong"
    strategy: str = "auto"      # "auto" | "target"
    target: str | None = None   # "A1"…"C1" si strategy="target"


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
    - applique la pipeline de simplification
    - analyse le texte original + texte simplifié (CECRL + fréquence)
    - renvoie toutes les infos attendues par le frontend
    """
    original = (req.text or "").strip()

    # 1) Simplification (pipeline principale)
    simp_result = simplify_text(
        text=original,
        mode=req.mode,
        strategy=req.strategy,
        target=req.target,
    )
    simplified = simp_result.get("simplified", "").strip()

    # 2) Analyse CECRL + fréquence sur original et simplifié
    analysis_original = analyze_text(original) if original else None
    analysis_simplified = analyze_text(simplified) if simplified else None

    # 3) Construction de la réponse pour le frontend
    return {
        "original": simp_result.get("original", original),
        "simplified": simplified,
        "mode": simp_result.get("mode"),
        "strategy": simp_result.get("strategy"),
        "target_level": simp_result.get("target_level"),
        "max_len": simp_result.get("max_len"),
        "strategy_explanation": simp_result.get("strategy_explanation"),

        "analysis_original": analysis_original,
        "analysis_simplified": analysis_simplified,
    }