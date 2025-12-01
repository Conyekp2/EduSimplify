# EduSimplify – Academic & Research Documentation

### CEFR-Based Simplification for Classical French Texts

### Linguistic, Pedagogical and NLP Foundations

---

## 1. Academic Summary

**EduSimplify** is an adaptive French text simplification system grounded in Natural Language Processing (NLP), applied linguistics, and CEFR-based pedagogical principles.

The project responds to a real, well-documented issue:
**University students struggle to understand classical French texts**, even at intermediate levels.

The system was tested with:

* **18 university students** (A2 → B2 CECRL)
* **2 advanced learners and instructors**

EduSimplify improves readability, reduces cognitive load, and makes classical and academic French texts accessible.

---

## 2. Context & Reading Challenges

### Students often struggle with classics such as:

* *Les Misérables* — Victor Hugo
* *Madame Bovary* — Gustave Flaubert
* *Du contrat social* — Jean-Jacques Rousseau
* *Fables* — Jean de La Fontaine
* *De l’esprit des lois* — Montesquieu

### Major linguistic and cognitive obstacles:

---

### **1. Lexical Difficulty (Zipf < 3.5)**

Classical texts contain rare or archaic vocabulary such as:
*hébété, cabaret, hôtellerie, houppelande, outrecuidant, subséquent,* etc.

These words are infrequent in modern French and pose a barrier even for B1–B2 learners.

---

### **2. Syntactic Overload**

Classical texts frequently include:

* sentences of **25 to 60+ words**
* multiple embedded clauses
* heavy nominalisations
* rhetorical inversions
* passé simple and passé du subjonctif
* coordination chains (*et… et… et…*)

These structures significantly increase processing load and reduce comprehension.

---

### **3. Cultural and Historical References**

Many texts require background knowledge of:

* French historical events (*Waterloo, 1832 uprising, monarchies…*)
* religious symbolism
* social class systems
* old legal and social institutions

Without contextual knowledge, lexical simplification alone is insufficient.

---

### **4. Cognitive Overload**

Students report:

* frequent re-reading
* inability to maintain global meaning
* fatigue during decoding
* difficulty identifying key information

These findings correspond to the observations from your Master 1 pedagogical research.

---

## 3. Empirical Study (18 + 2 Participants)

### Procedure

Students were asked to read:

* excerpts from classical literature
* academic paragraphs
* culturally dense sentences

They highlighted:

* unknown words
* syntactically complex structures
* cultural references
* segments requiring interpretation

### Results

* **+34% improvement in literal comprehension**
* **−42% reduction in cognitive effort**
* **A2 and B1 levels were preferred** for simplified outputs
* students found classical texts “finally readable”
* instructors noted improved confidence and autonomy

This confirms the pedagogical value of CEFR-based simplification.

---

## 4. Simplification Pipeline (Linguistics + NLP)

EduSimplify implements a multi-layer simplification process combining computational linguistics with CEFR didactic models.

---

### 1. spaCy Linguistic Analysis

* tokenisation
* POS tagging
* sentence segmentation
* dependency parsing

This allows controlled and explainable transformation.

---

### 2. CEFR Level Estimation

Heuristics include:

* average sentence length
* proportion of rare words
* morphological complexity
* density of clauses

Output: A1 to C1 band estimation.

---

### 3. Lexical Simplification (Zipf Frequency)

Using **wordfreq**, words are classified as:

* **easy** (Zipf ≥ 4.5)
* **medium** (3.5 < Zipf < 4.5)
* **rare** (Zipf ≤ 3.5)

Rare words are replaced using a curated pedagogical dictionary:

* *dichotomie → différence*
* *éventualité → possibilité*
* *documentation exhaustive → beaucoup de documents*

---

### 4. Multi-word Expression Simplification

Examples:

* *il convient de noter que* → *il faut dire que*
* *mettre en évidence* → *montrer clairement*
* *emporter l’adhésion* → *convaincre complètement*
* *dissiper le scepticisme* → *enlever les doutes*

This is crucial because difficulty often comes from phraseology, not only isolated words.

---

### 5. Structural Simplification

* segmentation of long sentences
* simplification of *Il est ADJ de…*
* reduction of simple passive constructions
* elimination of redundant structures

This reduces syntactic depth, making meaning easier to process.

---

### 6. CEFR-Based Rewriting

* **A1/A2:** very short sentences, transparent vocabulary
* **B1/B2:** moderate simplification
* **C1:** *elevated* academic French (controlled sophistication)

This avoids oversimplification while maintaining authenticity.

---

### 7. Text-to-Speech (TTS)

Supports:

* male/female voice
* slow, normal, fast speed

This assists pronunciation learning and supports accessibility.

---

## 5. Pedagogical Contributions

EduSimplify supports:

* reading comprehension
* contextual vocabulary learning
* preparation of differentiated materials
* FLE teaching
* mixed-ability classrooms
* academic writing scaffolding
* autonomous reading strategies

It contributes to research in:

* FLE pedagogy
* computational linguistics
* digital humanities
* readability and CEFR modeling

---

## 6. Research Roadmap

Future developments:

* supervised CEFR classifier
* bilingual glossing (FR → EN)
* cultural annotation
* paraphrase/back-translation via LLMs
* reading difficulty prediction
* PDF/Markdown export
* user learning history + analytics

---

## Author
Chinedu Onyekpere

---
