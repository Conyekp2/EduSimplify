import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "user", "content": "Simplify: Je vais à l'école."}
    ]
)

print(response["message"]["content"])