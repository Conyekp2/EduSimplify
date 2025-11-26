<p align="center">
  <img src="https://raw.githubusercontent.com/Conyekp2/EduSimplify/main/logo.png" alt="EduSimplify Logo" width="120">
</p>

<h1 align="center">EduSimplify</h1>

<p align="center">
  <strong>French text simplification + CEFR analysis + text-to-speech for language learners</strong><br>
  <em>Built for real learners, teachers and EdTech use cases.</em>
</p>

---

## What is EduSimplify?

EduSimplify is a small **NLP-powered web app** that helps French learners and teachers:

- **Simplify French texts** using rule-based + frequency-based transformations  
- **Estimate CEFR level** (A1–C1) of the original and simplified text  
- **Highlight difficult words** based on frequency (wordfreq)  
- **Read the simplified text aloud** (Text-to-Speech) with speed and voice options  

It is designed as a **practical, didactics-aware tool** for:
- teachers preparing materials at the right level  
- learners who want to understand “why this text feels hard”  
- EdTech experiments in explainable, rule-based simplification

---

## Main Features

- 🔍 **CEFR-like difficulty analysis**  
  - Heuristics using sentence length, lexical frequency, and rare word proportion  
  - Returns an estimated level (A1–C1) + a band (e.g. A2–B1) + explanation text  

- **Rule-based text simplification**  
  - Simplifies **connectors** (cependant → mais, nonobstant → malgré…)  
  - Rewrites some **heavy academic / administrative expressions** into simpler language  
  - Uses **word frequency (wordfreq)** to replace rare words when possible  
  - Adapts behaviour depending on **target level** (A1, A2, B1, B2, C1) and **mode** (light / standard / strong)

- 🗺️ **Two strategies**  
  - `auto` → choose a target level automatically based on the original text  
  - `target` → user selects an explicit CEFR level (A1–C1) for the simplification

- 🎨 **Visual lexical feedback**  
  - Original text is highlighted according to lexical difficulty:  
    - green = frequent words  
    - yellow = medium frequency  
    - red = rare words (potentiellement difficiles)

- 🔊 **Text-to-Speech for the simplified text**  
  - Uses browser’s SpeechSynthesis API  
  - **Speed options**: slow, normal, fast  
  - **Voice preference**: automatic, “female”, “male” (best-effort based on available voices)  

---

## How it works (NLP / Didactics)

Under the hood:

- **spaCy** (`fr_core_news_sm`)  
  - sentence segmentation  
  - POS tags and lemmas  
  - used both for simplification rules and CEFR-like analysis  

- **wordfreq**  
  - word frequency scores on Zipf scale (0–7)  
  - defines “easy / medium / hard” words  
  - used to mark rare words and decide candidates for substitution  

- **Custom rules / patterns**  
  - multi-word expressions:  
    - *« il convient de noter que » → « il faut dire que »*  
    - *« la dichotomie entre » → « la différence entre »*  
  - structural patterns:  
    - *« Il est ADJ de… » → C’est ADJ de / C’est ADJ. On doit…* depending on level  
    - some **simple passive** forms → *« est fait par »* for lower levels  

- **CEFR-like heuristic**  
  - counts sentences and tokens  
  - average sentence length  
  - ratio of rare words (“hard”)  
  - maps these indicators to a rough CEFR estimate (for demo/prototype use, not for official certification)

This is intentionally **transparent and rule-based**, so it can be discussed with teachers and learners.

---

## Demo workflow

1. Paste a French text (e.g. from news, literature, exam prep).  
2. Choose:
   - **Mode**: light / standard / strong  
   - **Strategy**: automatic vs specific CEFR target  
3. Click **“⚙️ Simplifier et analyser”**  
4. See:
   - CEFR box with estimated level + description  
   - Original text with coloured lexical difficulty  
   - Simplified version with its own CEFR estimation  
   - Strategy explanation (how / why the simplifier decided)  
5. Optionally click **“🔊 Lire le texte simplifié”** and adjust speed or voice.

---

## 🛠️ Tech Stack

- **Backend**
  - Python 3.10+
  - FastAPI
  - spaCy (`fr_core_news_sm`)
  - wordfreq

- **Frontend**
  - Vanilla HTML + CSS + JavaScript
  - Fetch API for communication with FastAPI
  - Browser Text-to-Speech (SpeechSynthesis)

---

## Run the project locally

### 1. Clone the repository

```bash
git clone https://github.com/Conyekp2/EduSimplify.git
cd EduSimplify
```
### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows (PowerShell / CMD)
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```
### 4. Start the FastAPI server
```bash
uvicorn app.main:app --reload
```
### 5. Open the web interface
```bash
http://127.0.0.1:8000/static/index.html
```
## Project structure
```bash
EduSimplify/
├─ app/
│  ├─ __init__.py
│  ├─ main.py        # FastAPI app (API + static file serving)
│  ├─ simplify.py    # Simplification pipeline (rules + frequency)
│  └─ cefr.py        # CEFR-like analysis + lexical difficulty
├─ static/
│  └─ index.html     # Frontend UI (textarea, controls, results, TTS)
├─ requirements.txt  # Python dependencies
├─ .gitignore
└─ README.md
```

## Author
Chinedu Onyekpere
Multilingual NLP practitioner & EdTech-oriented language teacher.
Focus: NLP for learning, CEFR-aligned tools, explainable simplification.

GitHub: https://github.com/Conyekp2

LinkedIn: https://www.linkedin.com/in/chinedu-onyekpere-5a89912a4/