from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .simplify import simplify_text
from pathlib import Path

app = FastAPI(title="EduSimplify")

# Serve the static folder (for our HTML page)
static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Allow requests from anywhere (useful in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplifyIn(BaseModel):
    text: str

class SimplifyOut(BaseModel):
    original: str
    simplified: str

@app.get("/")
def root():
    return {"message": "EduSimplify API is running. Open /static/index.html for the UI."}

@app.post("/api/simplify", response_model=SimplifyOut)
def api_simplify(payload: SimplifyIn):
    """
    Receive a text and return the original and simplified version.
    """
    return simplify_text(payload.text)