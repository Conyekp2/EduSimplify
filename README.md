# EduSimplify 🇫🇷

EduSimplify is a small web app that **simplifies French text** for language learners.  
It takes a paragraph in French and returns a version with:

- simpler logical connectors (ex. *cependant* → *mais*, *par conséquent* → *donc*)  
- long sentences split into shorter ones

This project combines ybackground in **FLE / didactics** and **NLP** in a concrete, usable tool.

---

## ✨ Features

- ✅ Web interface where you can paste any French text
- ✅ Rule-based simplification of frequent complex connectors
- ✅ Automatic splitting of long sentences into shorter chunks
- ✅ FastAPI backend + spaCy French model (`fr_core_news_sm`)
- ✅ Clean structure ready for extension (extra rules, levels, etc.)

---

## ⚙️ How it works (simplified)

1. The user submits a French text from the browser.
2. The frontend sends the text to the FastAPI endpoint `/api/simplify`.
3. The backend:
   - replaces “difficult” connectors with simpler equivalents
   - splits very long sentences into shorter ones using commas as break points
4. The simplified text is sent back and displayed in the interface.

This is a **first version**, focused on being clear, explainable and easy to extend.

---
## Run the project locally
### 1. Create and activate a virtual environment
```text
python3 -m venv .venv
source .venv/bin/activate
```
### 2. Install dependencies
```text
pip install -r requirements.txt
python3 -m spacy download fr_core_news_sm
```
### 3. Start the FastAPI server
```text
uvicorn app.main:app --reload
```
### 4. Open the web interface
```text
http://127.0.0.1:8000/static/index.html
```

## 📁 Project structure

```text
EduSimplify/
├─ app/
│  ├─ __init__.py
│  ├─ main.py          # FastAPI app (API + static files)
│  └─ simplify.py      # Simplification logic (connectors + splitting)
├─ static/
│  └─ index.html       # Minimal frontend (textarea + button + result)
├─ requirements.txt    # Python dependencies
├─ .gitignore          # Files to ignore in Git
└─ README.md           # Project documentation
```

