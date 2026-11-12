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

http_client = httpx.AsyncClient()

# --- STARTUP: Register Webhook ---
def set_webhook():
    url = f"{TELEGRAM_API_URL}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})
    print(response.json())

if __name__ == "__main__":
    set_webhook()