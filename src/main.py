import os
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Header, status
from chatbot_gemini import chatbot
from workers import env

load_dotenv()

BOT_TOKEN = getattr(env, "BOT_TOKEN", None)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

    
app = FastAPI()
http_client = httpx.AsyncClient()


    
async def send_telegram_message(chat_id: int, text: str):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"  # Optional: allows **bold**, *italic*, `code`, etc.
    }
    
    async with httpx.AsyncClient() as client:
        print("message is: ", text)
        response = await client.post(url, json=payload)
        return response.json()
    
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"].get("text", "")
        # response = chatbot(user_text)
        res = await send_telegram_message(chat_id, "hello")
        print(f"Chat ID from message: {chat_id}")
        
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the HTTP client session when the server stops."""
    await http_client.aclose()