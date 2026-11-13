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

load_dotenv()

# CREDENTIALS_PATH = getattr(env, "CREDENTIALS_PATH", None)
# TOKEN_PATH = getattr(env, "TOKEN_PATH", None)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def calendar():
  """Gets the first ten events of the user in the calendar. 
  Use this tool whenever the user asks for their upcoming events
  """

  
  # token_info = json.loads(getattr(env, "TOKEN_JSON", None))   # use your actual variable name
  # token_info = os.getenv("TOKEN_JSON")
  # creds = Credentials.from_authorized_user_info(token_info, SCOPES)
  token_info = json.loads(getattr(env, "TOKEN_JSON", None))   # use your actual variable name
  # token_info = os.getenv("TOKEN_JSON")
  creds = Credentials.from_authorized_user_info(token_info, SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    # else:
    #   flow = InstalledAppFlow.from_client_secrets_file(
    #       CREDENTIALS_PATH, SCOPES
    #   )
    #   creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    # with open(TOKEN_PATH, "w") as token:
    #   token.write(creds.to_json())
  # if os.path.exists(TOKEN_PATH):
  #   creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
  # if not creds or not creds.valid:
  #   if creds and creds.expired and creds.refresh_token:
  #     creds.refresh(Request())
  #   else:
  #     flow = InstalledAppFlow.from_client_secrets_file(
  #         CREDENTIALS_PATH, SCOPES
  #     )
  #     creds = flow.run_local_server(port=0)
  #   # Save the credentials for the next run
  #   with open(TOKEN_PATH, "w") as token:
  #     token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
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