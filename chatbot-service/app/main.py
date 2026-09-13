import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_cpp import Llama

app = FastAPI()

MODEL_PATH = os.getenv("MODEL_PATH", "/app/app/model/Syne-Coder-V2.gguf")

llm = None

@app.on_event("startup")
def load_model():
    global llm
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=os.cpu_count() or 4,
        n_gpu_layers=0
    )

class ChatRequest(BaseModel):
    messages: list
    temperature: float = 0.1
    max_tokens: int = 2048
    stream: bool = True

def format_prompt(messages):
    """
    Construit un prompt simple à partir des messages.
    Vous pouvez aussi utiliser le chat template intégré du modèle,
    mais cette méthode fonctionne pour la plupart des modèles.
    """
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"System: {content}\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"
    return prompt

@app.post("/api/ln/chat/completions")
async def chat_completion(request: ChatRequest):
    prompt = format_prompt(request.messages)

    if request.stream:
        async def generate():
            # llama-cpp-python supporte stream=True pour générer token par token
            for chunk in llm(
                prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True
            ):
                text = chunk["choices"][0]["text"]
                if text:
                    # Envoi au format OpenAI (delta)
                    data = json.dumps({"choices": [{"delta": {"content": text}}]})
                    yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    # Mode non streamé (si stream=False)
    output = llm(
        prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    text = output["choices"][0]["text"]
    return {"choices": [{"message": {"content": text}}]}