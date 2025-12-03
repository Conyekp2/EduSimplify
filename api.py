from fastapi import FastAPI
import ollama

app = FastAPI()

@app.get("/")
def home():
    return {"message": "EduSimplify API is running"}

@app.post("/simplify")
def simplify_text(payload: dict):
    text = payload.get("text", "")

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "user", "content": f"Simplify this: {text}"}
        ]
    )

    simplified = response["message"]["content"]
    return {"simplified_text": simplified}
