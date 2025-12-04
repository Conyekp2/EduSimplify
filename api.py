from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import ollama

app = FastAPI()

# Serve the frontend from "static" folder (relative path)
app.mount("/static", StaticFiles(directory="static"), name="static")


class SimplifyRequest(BaseModel):
    text: str
    target_level: str | None = None  # "A1"–"C1" or None


CEFR_EXPLANATIONS = {
    "A1": (
        "A1 level: very short sentences, present tense, concrete everyday words "
        "(family, school, basic needs). No complex connectors or abstract ideas."
    ),
    "A2": (
        "A2 level: simple sentences about everyday life, simple past and future, "
        "frequent vocabulary. Limited use of connectors like 'mais', 'parce que'."
    ),
    "B1": (
        "B1 level: longer sentences, some complex structures, opinions and justifications, "
        "more varied vocabulary but still understandable for independent learners."
    ),
    "B2": (
        "B2 level: complex sentences with subordination, abstract topics, idiomatic expressions "
        "and nuanced connectors (cependant, néanmoins, pourtant…)."
    ),
    "C1": (
        "C1 level: dense, highly nuanced text, flexible use of language, implicit meanings "
        "and rich connectors typical of advanced academic or literary style."
    ),
}


@app.get("/")
def home():
    return {"message": "EduSimplify API is running"}


@app.post("/simplify")
def simplify_text(req: SimplifyRequest):
    text = req.text
    target_level = req.target_level  # e.g. "A2" if the user chose target level

    if not text.strip():
        return {
            "simplified_text": "",
            "target_level": target_level,
            "cefr_explanation": "Empty text, no CEFR evaluation.",
        }

    # Build the prompt dynamically: with or without target CEFR level
    if target_level:
        system_prompt = (
            f"Tu es un expert en FLE. Simplifie le texte suivant pour un niveau {target_level} du CECR.\n"
            "Règles :\n"
            "- Ne change pas le sens.\n"
            "- Utilise des phrases simples.\n"
            "- Utilise un vocabulaire adapté au niveau cible.\n"
            "- N’ajoute pas d’informations.\n"
            "Donne uniquement la version simplifiée."
        )
    else:
        system_prompt = (
            "Tu es un expert en FLE. Simplifie le texte suivant pour un public d'apprenants.\n"
            "Règles :\n"
            "- Ne change pas le sens.\n"
            "- Utilise des phrases plus simples.\n"
            "- Réduis les tournures trop complexes.\n"
            "- N’ajoute pas d’informations.\n"
            "Donne uniquement la version simplifiée."
        )

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\nTexte : {text}"},
            ],
        )
        simplified = response["message"]["content"]

        # Explanation for the chosen level (or generic explanation)
        if target_level and target_level in CEFR_EXPLANATIONS:
            expl = CEFR_EXPLANATIONS[target_level]
        elif target_level:
            expl = f"Target level {target_level} selected. The text is simplified to match its typical sentence length and vocabulary range."
        else:
            expl = (
                "No specific CEFR target selected. The text was simplified globally "
                "to make it more accessible to learners."
            )

        return {
            "simplified_text": simplified,
            "target_level": target_level,
            "cefr_explanation": expl,
        }

    except Exception as e:
        print("Error calling Ollama:", repr(e))
        return {
            "simplified_text": "Error: could not contact Ollama backend.",
            "target_level": target_level,
            "cefr_explanation": "An error occurred while generating the simplification.",
        }