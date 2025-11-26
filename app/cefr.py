import math
from collections import Counter
from typing import Dict, List, Any

import spacy
from wordfreq import zipf_frequency

# Chargement du modèle français
try:
    nlp_cefr = spacy.load("fr_core_news_sm")
except OSError:
    from spacy.cli import download
    download("fr_core_news_sm")
    nlp_cefr = spacy.load("fr_core_news_sm")


def _compute_word_difficulty(text: str) -> List[Dict[str, Any]]:
    """
    Calcule la difficulté lexicale mot par mot avec wordfreq (échelle de Zipf).
    Retourne une liste de dicts :
    {form, lemma, count, zipf, difficulty}
    difficulty ∈ {"easy","medium","hard"}
    """
    doc = nlp_cefr(text)
    tokens = [t for t in doc if t.is_alpha]

    if not tokens:
        return []

    counter = Counter([t.text for t in tokens])
    results = []

    for form, count in counter.items():
        z = zipf_frequency(form, "fr")  # 0–7
        # Classement simple :
        #   >= 4.0  → easy (fréquent)
        #   3.0–4.0 → medium
        #   < 3.0   → hard (rare)
        if z >= 4.0:
            diff = "easy"
        elif z >= 3.0:
            diff = "medium"
        else:
            diff = "hard"

        # On récupère au moins un lemma pour ce form
        lemma = form.lower()
        for t in tokens:
            if t.text == form:
                lemma = t.lemma_.lower()
                break

        results.append(
            {
                "form": form,
                "lemma": lemma,
                "count": count,
                "zipf": float(z),
                "difficulty": diff,
            }
        )

    # On renvoie trié par difficulté puis par fréquence (hard d'abord)
    def sort_key(w):
        order = {"hard": 0, "medium": 1, "easy": 2}
        return (order.get(w["difficulty"], 1), -w["count"])

    return sorted(results, key=sort_key)


def _estimate_level(sentences: int, tokens: int, avg_len: float, hard_ratio: float) -> Dict[str, Any]:
    """
    Heuristique CECRL simple basée sur :
    - longueur moyenne de phrase
    - proportion de mots rares ("hard")
    Retourne :
    {
      "estimated_level": "B1",
      "level_band": ["A2","B1"],
      "level_band_explanation": "...",
      "explanation": "..."
    }
    """
    if tokens == 0:
        return {
            "estimated_level": "A1",
            "level_band": ["A1", "A2"],
            "level_band_explanation": "Texte trop court pour une analyse fiable. On suppose un niveau débutant.",
            "explanation": "Texte vide ou presque vide.",
        }

    # Règles heuristiques (tu pourras affiner plus tard)
    # Combinaison de complexité et de vocabulaire
    if tokens <= 5:
        level = "A1"
        band = ["A1", "A2"]
        band_expl = "Texte très court avec phrases très simples et vocabulaire de base."
    else:
        if hard_ratio > 0.18 or avg_len > 24:
            level = "C1"
            band = ["B2", "C1"]
            band_expl = "Beaucoup de mots rares ou de phrases longues : texte très exigeant."
        elif hard_ratio > 0.12 or avg_len > 20:
            level = "B2"
            band = ["B1", "B2"]
            band_expl = "Vocabulaire relativement riche et phrases assez longues."
        elif hard_ratio > 0.07 or avg_len > 16:
            level = "B1"
            band = ["A2", "B1"]
            band_expl = "Complexité moyenne avec quelques mots moins fréquents."
        elif hard_ratio > 0.03 or avg_len > 12:
            level = "A2"
            band = ["A1", "A2"]
            band_expl = "Phrases courtes, peu de mots rares, mais un peu au-dessus du niveau débutant."
        else:
            level = "A1"
            band = ["A1", "A2"]
            band_expl = "Phrases courtes, vocabulaire très fréquent : niveau débutant."

    explanation = (
        f"Niveau estimé {level} basé sur une longueur moyenne de {avg_len:.1f} mots "
        f"et une proportion de mots rares d’environ {hard_ratio*100:.1f} %."
    )

    return {
        "estimated_level": level,
        "level_band": band,
        "level_band_explanation": band_expl,
        "explanation": explanation,
    }


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyse CECRL + lexicale pour un texte donné.
    Retourne un dict conforme à ce qu'attend le frontend :
    {
      "estimated_level": ...,
      "sentences": ...,
      "tokens": ...,
      "avg_sentence_length": ...,
      "word_difficulty": [...],
      "level_band": [...],
      "level_band_explanation": "...",
      "explanation": "..."
    }
    """
    text = (text or "").strip()
    if not text:
        return {
            "estimated_level": "A1",
            "sentences": 0,
            "tokens": 0,
            "avg_sentence_length": 0.0,
            "word_difficulty": [],
            "level_band": ["A1", "A2"],
            "level_band_explanation": "Texte vide. On considère un niveau débutant par défaut.",
            "explanation": "Aucune phrase à analyser.",
        }

    doc = nlp_cefr(text)

    # Phrases & tokens
    sents = list(doc.sents)
    sentences = len(sents)
    tokens_all = [t for t in doc if not t.is_space]
    tokens = len(tokens_all)

    if sentences > 0:
        avg_len = tokens / sentences
    else:
        avg_len = float(tokens)

    # Difficulté lexicale
    word_difficulty = _compute_word_difficulty(text)
    hard_tokens_count = sum(w["count"] for w in word_difficulty if w["difficulty"] == "hard")
    total_alpha_tokens = sum(w["count"] for w in word_difficulty)
    hard_ratio = hard_tokens_count / total_alpha_tokens if total_alpha_tokens > 0 else 0.0

    # Estimation de niveau
    level_info = _estimate_level(sentences, tokens, avg_len, hard_ratio)

    result = {
        "estimated_level": level_info["estimated_level"],
        "sentences": sentences,
        "tokens": tokens,
        "avg_sentence_length": float(avg_len),
        "word_difficulty": word_difficulty,
        "level_band": level_info["level_band"],
        "level_band_explanation": level_info["level_band_explanation"],
        "explanation": level_info["explanation"],
    }

    return result
