import re
from typing import Optional

import spacy
from wordfreq import zipf_frequency

from .cefr import analyze_text

# -------------------------------------------------
# 0. Chargement du modèle spaCy
# -------------------------------------------------
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    from spacy.cli import download
    download("fr_core_news_sm")
    nlp = spacy.load("fr_core_news_sm")


# -------------------------------------------------
# 1. RÉÉCRITURE C1 (style plus soutenu)
# -------------------------------------------------

def elevate_for_c1(text: str) -> str:
    """
    Réécritures plus soutenues pour le niveau C1.
    Ce bloc peut être enrichi progressivement avec d'autres motifs.
    """
    replacements = [
        ("Je vais à l'école", "Je me rends à l'école"),
        ("Je vais à l’ecole", "Je me rends à l’ecole"),
        ("Je vais à l’école", "Je me rends à l’école"),
        ("je vais à l'école", "je me rends à l'école"),
        ("je vais à l’ecole", "je me rends à l’ecole"),
        ("je vais à l’école", "je me rends à l’école"),
    ]

    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


# -------------------------------------------------
# 2. CONNECTEURS & DÉCOUPAGE DE PHRASES
# -------------------------------------------------

EASY_CONNECTORS = {
    "cependant": "mais",
    "toutefois": "mais",
    "néanmoins": "mais",
    "par conséquent": "donc",
    "en conséquence": "donc",
    "ainsi": "donc",
    "tandis que": "alors que",
    "afin que": "pour que",
    "afin de": "pour",
    "lorsque": "quand",
    "désormais": "maintenant",
    "nonobstant": "malgré",
    "attendu que": "parce que",
}


def simplify_connectors(text: str) -> str:
    """
    Remplace certains connecteurs plus difficiles par des équivalents plus simples.
    Garde la majuscule si le mot original commence par une majuscule.
    """
    out = text
    for hard, easy in EASY_CONNECTORS.items():
        pattern = r"\b" + re.escape(hard) + r"\b"

        def repl(m):
            original = m.group(0)
            if original[0].isupper():
                return easy.capitalize()
            return easy

        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def split_long_sentences(text: str, max_len: int = 22) -> str:
    """
    Découpe les phrases longues aux virgules/points-virgules pour respecter une longueur maximale.
    max_len = nombre maximum de mots par segment.
    """
    temp_text = text.replace(";", ",")
    doc = nlp(temp_text)
    new_sents = []

    for sent in doc.sents:
        parts = [p.strip() for p in sent.text.split(",")]
        chunk = ""

        for p in parts:
            if not p:
                continue
            p_tokens = p.split()
            if not p_tokens:
                continue

            current_len = len(chunk.split()) if chunk else 0
            if current_len + len(p_tokens) > max_len:
                if chunk:
                    new_sents.append(chunk.strip())
                chunk = p
            else:
                chunk = (chunk + ", " + p) if chunk else p

        if chunk:
            new_sents.append(chunk.strip())

    fixed = []
    for s in new_sents:
        s = s.rstrip(",.; ").strip()
        if not s:
            continue
        if s.endswith((".", "!", "?")):
            fixed.append(s)
        else:
            fixed.append(s + ".")
    return " ".join(fixed)


# -------------------------------------------------
# 3. LEXIQUE : fréquence + substitutions
# -------------------------------------------------

LEXICAL_SUBSTITUTIONS = {
    "dichotomie": "différence",
    "impératif": "très important",
    "souligner": "dire clairement",
    "circonspection": "prudence",
    "prétendre": "dire",
    "éventualité": "possibilité",
    "subséquent": "suivant",
    "tenace": "forte",
    "outrecuidant": "arrogant",
    "s'avérer": "être",
    "conceptuel": "abstrait",
    # verbes "lourds"
    "effectuer": "faire",
    "procéder": "faire",
    "réaliser": "faire",
    "conduire": "faire",
    "considérer": "penser",
    "susciter": "causer",
    "déceler": "trouver",
    "recenser": "compter",
    "dépourvu": "sans",
    "subsister": "rester",
    "interroger": "demander",
    "exiger": "demander",
}


def apply_lexical_rules(text: str, target_level: Optional[str]) -> str:
    """
    Substitution lexicale guidée par la fréquence des mots et le niveau cible.
    - Pour A1/A2/B1 : on vise les mots rares (Zipf <= 3.5) parmi NOUN/ADJ/ADV/VERB,
      lorsqu'ils ont une substitution connue.
    - Pour B2/C1 : on laisse le lexique plus riche.
    """
    if target_level is None:
        return text

    target_level = target_level.upper()
    if target_level not in {"A1", "A2", "B1"}:
        return text

    doc = nlp(text)
    new_tokens = []

    for token in doc:
        form = token.text
        lemma = token.lemma_.lower()

        if not token.is_alpha:
            new_tokens.append(token.text_with_ws)
            continue

        z = zipf_frequency(form, "fr")  # 0–7 sur échelle de Zipf

        if token.pos_ in {"NOUN", "ADJ", "ADV", "VERB"} and z > 0 and z <= 3.5:
            replacement = (
                LEXICAL_SUBSTITUTIONS.get(lemma)
                or LEXICAL_SUBSTITUTIONS.get(form.lower())
            )
            if replacement:
                if form[0].isupper():
                    replacement = replacement.capitalize()
                new_tokens.append(replacement + token.whitespace_)
            else:
                new_tokens.append(token.text_with_ws)
        else:
            new_tokens.append(token.text_with_ws)

    return "".join(new_tokens).strip()


# -------------------------------------------------
# 4. EXPRESSIONS PHRASEOLOGIQUES (multi-mots)
# -------------------------------------------------

PHRASAL_SUBSTITUTIONS = {
    # 1. Expressions argumentatives / académiques
    "il convient de noter que": "il faut dire que",
    "il est essentiel de souligner que": "c'est très important de dire que",
    "il est impératif de": "il faut vraiment",
    "il va de soi que": "c'est évident que",
    "il ressort de cette analyse que": "on voit que",
    "on observe une tendance à": "on voit souvent que",
    "on peut en déduire que": "on peut comprendre que",
    "à première vue": "au début",
    "en d’autres termes": "pour dire simplement",
    "en d'autres termes": "pour dire simplement",
    "en définitive": "finalement",

    # 2. Simplification de subordonnées simples
    "qui est bruyant": "bruyant",
    "qui est important": "important",
    "qui est nécessaire": "nécessaire",
    "qui est essentiel": "essentiel",

    # 3. Expressions juridiques / administratives
    "l'éloquence de son plaidoyer": "le fait qu'il parle très bien",
    "l’eloquence de son plaidoyer": "le fait qu'il parle très bien",
    "l’éloquence de son plaidoyer": "le fait qu'il parle très bien",
    "documentation exhaustive": "beaucoup de documents",
    "documentation très exhaustive": "beaucoup de documents",
    "dissiper le scepticisme": "enlever les doutes",
    "dissiper le scepticisme initial": "enlever les premiers doutes",
    "emporter son adhésion": "le convaincre complètement",
    "emporter l'adhésion du jury": "convaincre complètement le jury",
    "emporter l’adhésion du jury": "convaincre complètement le jury",
    "être soumis à une réglementation": "devoir suivre une règle",
    "être en conformité avec": "respecter",
    "porter atteinte à": "causer un problème",
    "être tenu responsable": "être responsable",
    "faire l'objet de": "être concerné par",
    "entrer en vigueur": "commencer officiellement",

    # 4. Expressions abstraites / intellectuelles
    "la dichotomie entre": "la différence entre",
    "le postulat initial": "l'idée de départ",
    "le raisonnement sous-jacent": "l'idée cachée",
    "les implications de ce phénomène": "ce que cela change",
    "une perspective nuancée": "une idée plus précise",
    "les enjeux majeurs": "les choses importantes",
    "les facteurs déterminants": "les choses qui changent tout",
    "un constat alarmant": "une situation inquiétante",
    "une approche holistique": "une vision générale",
    "un contexte favorable": "une bonne situation",

    # 5. Expressions émotionnelles / subjectives
    "susciter une vive réaction": "faire réagir fortement",
    "nourrir des inquiétudes": "donner des inquiétudes",
    "faire preuve de résilience": "être très fort et continuer",
    "témoigner d’une grande prudence": "être très prudent",
    "témoigner d'une grande prudence": "être très prudent",
    "se heurter à un refus": "recevoir un refus",
    "subir une pression considérable": "avoir beaucoup de pression",
    "manifester un intérêt marqué": "être très intéressé",
    "faire preuve d’empathie": "comprendre les autres",
    "faire preuve d'empathie": "comprendre les autres",
    "exprimer son désarroi": "dire qu'on est triste ou perdu",
    "tirer parti de": "utiliser pour avoir un avantage",

    # 6. Expressions techniques / scientifiques
    "mettre en évidence": "montrer clairement",
    "effectuer une analyse approfondie": "étudier beaucoup",
    "formuler une hypothèse": "donner une idée possible",
    "procéder à une comparaison": "comparer",
    "un échantillon représentatif": "un groupe qui montre bien la situation",
    "des données fiables": "des données sûres",
    "une corrélation significative": "un lien important",
    "une variation notable": "un changement important",
    "un résultat probant": "un bon résultat",
    "une méthodologie rigoureuse": "une façon de travailler organisée",

    # 7. Expressions sociales / économiques
    "être confronté à une crise": "avoir un gros problème",
    "accroître la productivité": "travailler mieux",
    "réduire les disparités": "réduire les différences",
    "favoriser l'inclusion": "aider tout le monde à participer",
    "renforcer la cohésion sociale": "aider les gens à bien vivre ensemble",
    "promouvoir l’égalité des chances": "donner les mêmes chances à tous",
    "promouvoir l'égalité des chances": "donner les mêmes chances à tous",
    "stimuler l’économie": "aider les entreprises à mieux travailler",
    "stimuler l'economie": "aider les entreprises à mieux travailler",
    "avoir un impact considérable": "changer beaucoup",
    "contribuer à l’amélioration de": "aider à améliorer",
    "contribuer à l'amelioration de": "aider à améliorer",
    "un secteur en pleine expansion": "un secteur qui grandit vite",
}


def apply_phrasal_rules(text: str, target_level: Optional[str]) -> str:
    """
    Simplification de groupes de mots (expressions figées, tournures académiques).
    On les applique surtout pour A1/A2/B1.
    """
    if target_level is None:
        return text

    target_level = target_level.upper()
    if target_level not in {"A1", "A2", "B1"}:
        # Pour B2/C1, on garde souvent ces expressions
        return text

    out = text
    for hard_expr, easy_expr in PHRASAL_SUBSTITUTIONS.items():
        pattern = r"\b" + re.escape(hard_expr) + r"\b"
        out = re.sub(pattern, easy_expr, out, flags=re.IGNORECASE)
    return out


# -------------------------------------------------
# 5. RÈGLES DE STRUCTURES TYPIQUES (patterns)
# -------------------------------------------------

ADJ_INTENSITY = {
    "impératif": "très important",
    "nécessaire": "important",
    "essentiel": "très important",
    "important": "important",
}


def apply_pattern_rules(text: str, target_level: Optional[str]) -> str:
    """
    Règles générales sur des structures typiques fréquentes :
    - 'Il est ADJ de...' -> simplifications selon le niveau
    - passif simple 'est réalisé/est effectué...' -> 'est fait par'
    - cas très simples de sujet répété
    """
    if target_level is None:
        return text

    target_level = target_level.upper()
    out = text

    # --- Règle : "Il est ADJ de" ---
    pattern_adj = r"\b[Ii]l est (\w+) de\b"

    def repl_adj(match: re.Match) -> str:
        adj = match.group(1).lower()
        intensity = ADJ_INTENSITY.get(adj, adj)

        if target_level in {"B1", "B2"}:
            # B1/B2 : "C'est important de ..."
            return f"C'est {intensity} de"
        elif target_level in {"A1", "A2"}:
            # A1/A2 : "C'est important. On doit ..."
            return f"C'est {intensity}. On doit"
        else:
            # C1 : on laisse la structure telle quelle
            return match.group(0)

    out = re.sub(pattern_adj, repl_adj, out)

    # Passif simple pour A1/A2 : "est réalisé/est effectué/est conduit/..." -> "est fait par"
    if target_level in {"A1", "A2"}:
        out = re.sub(
            r"\b[Ee]st (effectué|réalisé|conduit|demandé|étudié|analysé) par\b",
            "est fait par",
            out,
            flags=re.IGNORECASE,
        )

    # Cas très simple de sujet répété :
    # "Le chat court et le chat mange" -> "Le chat court et mange"
    out = re.sub(
        r"(\b\w+\s+)(et)\s+\1",
        r"\1\2 ",
        out,
        flags=re.IGNORECASE,
    )

    return out


# -------------------------------------------------
# 6. CONFIG NIVEAUX & STRATÉGIES
# -------------------------------------------------

LEVEL_CONFIG = {
    "A1": {"mode": "strong", "max_len": 8},
    "A2": {"mode": "strong", "max_len": 12},
    "B1": {"mode": "standard", "max_len": 18},
    "B2": {"mode": "standard", "max_len": 22},
    "C1": {"mode": "light", "max_len": 30},
}


def _resolve_strategy(
    original_text: str,
    mode: str,
    strategy: str,
    target: Optional[str],
):
    """
    Décide comment simplifier en fonction de :
    - mode ('light' / 'standard' / 'strong')
    - strategy ('auto' ou 'target')
    - target (A1–C1) si strategy='target'
    Retourne :
    - internal_mode : 'light'/'standard'/'strong'
    - target_level  : niveau cible CECRL (ou niveau estimé)
    - max_len       : longueur max de phrase
    - explanation   : explication textuelle de la stratégie
    """
    mode = (mode or "standard").lower()
    strategy = (strategy or "auto").lower()
    target = target.upper() if target else None

    allowed_levels = {"A1", "A2", "B1", "B2", "C1"}

    # 1) Niveau explicitement choisi
    if strategy == "target" and target in allowed_levels:
        conf = LEVEL_CONFIG[target]
        internal_mode = conf["mode"]
        max_len = conf["max_len"]

        if target == "C1":
            explanation = (
                "Simplification orientée vers le niveau C1 : "
                "conservation du sens, formulations plus soutenues et style plus formel."
            )
        elif target in {"A1", "A2"}:
            explanation = (
                f"Simplification orientée vers le niveau {target} : "
                f"phrases courtes, vocabulaire fréquent et structures simples."
            )
        else:
            explanation = (
                f"Simplification orientée vers le niveau {target} : "
                f"phrases d’environ {max_len} mots avec simplifications modérées."
            )

        return internal_mode, target, max_len, explanation

    # 2) Mode automatique
    if strategy == "auto":
        stats = analyze_text(original_text)
        orig_level = stats.get("estimated_level", "B1")

        mapping = {
            "C1": "B2",
            "B2": "B1",
            "B1": "A2",
            "A2": "A2",
            "A1": "A1",
        }
        target_level = mapping.get(orig_level, "B1")
        conf = LEVEL_CONFIG[target_level]
        internal_mode = conf["mode"]
        max_len = conf["max_len"]

        explanation = (
            f"Mode automatique : texte estimé {orig_level}, "
            f"simplifié vers un niveau proche de {target_level} "
            f"avec des phrases plus courtes et quelques simplifications lexicales."
        )
        return internal_mode, target_level, max_len, explanation

    # 3) Fallback
    default_max = 22
    explanation = (
        "Simplification basique selon le mode choisi, sans objectif CECRL explicite."
    )
    return mode, None, default_max, explanation


# -------------------------------------------------
# 7. FONCTION PRINCIPALE EXPOSÉE À L’API
# -------------------------------------------------

def simplify_text(
    text: str,
    mode: str = "standard",
    strategy: str = "auto",
    target: Optional[str] = None,
) -> dict:
    """
    Pipeline de simplification complet.

    - mode      : 'light' / 'standard' / 'strong'
    - strategy  : 'auto' (choix automatique du niveau) ou 'target'
    - target    : 'A1'..'C1' si strategy='target'
    """
    original_text = text.strip()

    if not original_text:
        return {
            "original": "",
            "simplified": "",
            "mode": mode,
            "strategy": strategy,
            "target_level": target,
            "max_len": 0,
            "strategy_explanation": "Texte vide.",
        }

    internal_mode, target_level, max_len, strategy_explanation = _resolve_strategy(
        original_text, mode, strategy, target
    )

    # Étape 1 : simplification des connecteurs
    simplified = simplify_connectors(original_text)

    # Étape 2 : réécriture de structures typiques (Il est ADJ de..., passif, etc.)
    simplified = apply_pattern_rules(simplified, target_level)

    # Étape 3 : simplification d'expressions figées / groupes de mots
    simplified = apply_phrasal_rules(simplified, target_level)

    # Étape 4 : simplification lexicale (A1/A2/B1, mode strong)
    if internal_mode == "strong":
        simplified = apply_lexical_rules(simplified, target_level)

    # Étape 5 : découpage des phrases longues
    if internal_mode in {"standard", "strong"}:
        simplified = split_long_sentences(simplified, max_len=max_len)

    # Étape 6 : réécriture C1 (style plus soutenu, si demandé)
    if target_level == "C1":
        simplified = elevate_for_c1(simplified)

    return {
        "original": original_text,
        "simplified": simplified.strip(),
        "mode": internal_mode,
        "strategy": strategy,
        "target_level": target_level,
        "max_len": max_len,
        "strategy_explanation": strategy_explanation,
    }
