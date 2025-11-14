import spacy

# Load the French model
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    from spacy.cli import download
    download("fr_core_news_sm")
    nlp = spacy.load("fr_core_news_sm")

# Simple connectors replacement
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
}

def simplify_connectors(text: str) -> str:
    out = text
    for hard, easy in EASY_CONNECTORS.items():
        out = out.replace(hard, easy)
        out = out.replace(hard.capitalize(), easy.capitalize())
    return out

def split_long_sentences(text: str, max_len: int = 22) -> str:
    """
    Split very long sentences into smaller ones using commas as break points.
    max_len is the maximum number of words per chunk.
    """
    doc = nlp(text)
    new_sents = []
    for sent in doc.sents:
        tokens = [t.text for t in sent]
        if len(tokens) <= max_len:
            new_sents.append(sent.text.strip())
        else:
            parts = [p.strip() for p in sent.text.split(",")]
            chunk = ""
            current_len = 0
            for p in parts:
                p_tokens = p.split()
                if current_len + len(p_tokens) <= max_len:
                    chunk = (chunk + ", " + p) if chunk else p
                    current_len += len(p_tokens)
                else:
                    if chunk:
                        new_sents.append(chunk.strip())
                    chunk = p
                    current_len = len(p_tokens)
            if chunk:
                new_sents.append(chunk.strip())
    return " ".join(s if s.endswith((".", "!", "?")) else s + "." for s in new_sents)

def simplify_text(text: str) -> dict:
    connectors = simplify_connectors(text)
    simplified = split_long_sentences(connectors, max_len=15)
    return {
        "original": text.strip(),
        "simplified": simplified.strip(),
    }
