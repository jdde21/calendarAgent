import os
import json
import datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from workers import env
from utils import get_access_token, gcall
from urllib.parse import urlencode

load_dotenv()

# CREDENTIALS_PATH = getattr(env, "CREDENTIALS_PATH", None)
# TOKEN_PATH = getattr(env, "TOKEN_PATH", None)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


async def calendar():
  """Gets the first ten events of the user in the calendar. 
  Use this tool whenever the user asks for their upcoming events
  """

  
  # token_info = json.loads(getattr(env, "TOKEN_JSON", None))   # use your actual variable name
  # token_info = os.getenv("TOKEN_JSON")
  # creds = Credentials.from_authorized_user_info(token_info, SCOPES)
  token_info = json.loads(getattr(env, "TOKEN_JSON", None))   # use your actual variable name
  # token_info = os.getenv("TOKEN_JSON")
  access_token = await get_access_token(token_info)

  

  try:
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    params = {"timeMin": now, "maxResults": 10, "singleEvents": "true", "orderBy": "startTime"}
    events_result_url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{urlencode(params)}"
    events_result = await gcall(events_result_url, access_token)
    events = events_result.get("items", [])

    if not events:
      return "No upcoming events found."

    events_list = []
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      events_list.append(f"{start}, {event["summary"]}")

    return events_list
  except HttpError as error:
    return(f"An error occurred: {error}")


if __name__ == "__main__":
  calendar()