import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class ChatRequest(BaseModel):
    message: str
    context: str = None

@router.post("/")
async def chat_with_assistant(request: ChatRequest):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API Key not configured.")

    try:
        # System prompt to define the persona
        system_prompt = (
            "You are Kaira AI, a specialized biodiversity and wildlife identification assistant. "
            "Your goal is to help users identify species, provide information about habitats, "
            "conservation status, and ecological importance. "
            "Be professional, encouraging, and scientific. "
            "If asked about something unrelated to biology or biodiversity, politely steer the conversation back."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8001", # Required for OpenRouter
            "X-Title": "Kaira AI Assistant", # Optional but good practice
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek/deepseek-r1", # Updated to DeepSeek R1
            "messages": messages
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        ai_message = data['choices'][0]['message']['content']
        
        return {"response": ai_message}

    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with AI assistant.")
