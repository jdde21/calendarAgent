import os.path
import inspect
from google import genai
from google.genai import types
from dotenv import load_dotenv
from calendar_tool import calendar
from classroom_tool import classroom
from workers import env



# GOOGLE_API_KEY = env.GOOGLE_API_KEY
GOOGLE_API_KEY = getattr(env, "GOOGLE_API_KEY", None)
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

prompt = "What are my events?"

async def chatbot(prompt):
    chat = client.aio.chats.create(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            tools=[calendar, classroom],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
    )
    tools = {"calendar": calendar, "classroom": classroom}
    response = await chat.send_message(prompt)

    # keep going while the model is asking for tools
    while response.function_calls:
        parts = []
        for fc in response.function_calls:
            fn = tools[fc.name]
            args = fc.args or {}
            try:
                if inspect.iscoroutinefunction(fn):
                    result = await fn(**args)
                else:
                    result = fn(**args)
                payload = {"result": result}
            except Exception as e:
                payload = {"error": str(e)}   # let the model see the failure
            parts.append(types.Part.from_function_response(name=fc.name, response=payload))
        response = await chat.send_message(parts)

    return response.text

if __name__ == "__main__":
    chatbot(prompt)