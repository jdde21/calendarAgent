import os
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header, status
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBHOOK_URL = "https://passion-hazing-plaster.ngrok-free.dev/webhook"

def remove_webhook():
    url = f"{TELEGRAM_API_URL}/deleteWebhook"
    
    # Optional: pass drop_pending_updates=True to clear queued messages sent while offline
    payload = {"drop_pending_updates": True}
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get("ok"):
        print("✅ Webhook deleted successfully!")
        print(f"Telegram response: {result.get('description')}")
    else:
        print("❌ Failed to delete webhook.")
        print(f"Error: {result}")

if __name__ == "__main__":
    remove_webhook()