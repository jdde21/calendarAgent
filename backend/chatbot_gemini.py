import os.path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from calendar_tool import calendar
from classroom_tool import main

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

prompt = "What are my events?"

def chatbot(prompt):
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            tools=[calendar],
        )
    )
    response1 = chat.send_message(prompt)
    return(response1.text)

if __name__ == "__main__":
    chatbot(prompt)