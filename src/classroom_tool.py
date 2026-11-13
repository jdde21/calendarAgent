import os
import json
import calendar
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from workers import env



# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
]
BASE = "https://classroom.googleapis.com/v1"

async def classroom():
  """Gets the tasks that are not yet done for each course. It returns
  a dict containing the course title as a key and a list containing strings 
  describing the course work as well as the deadline
  """

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  
  token_info = json.loads(env.TOKEN_JSON)
  access_token = await get_access_token(token_info)

  try:
    courses = []
    courseTitle = {}
    data = await gcall(f"{BASE}/courses?{urlencode({'studentId': 'me', 'pageSize': 50})}", access_token)
    request = data.get("courses", [])
    courses = courses + [course["id"] for course in request]
    courseTitle = courseTitle | {course["id"]: course["name"] for course in request}
    token = data.get("nextPageToken") 
    

    if token:
      data = await gcall(
          f"{BASE}/courses?{urlencode({'studentId': 'me', 'pageSize': 50, 'pageToken': token})}",
          access_token,
      )
      temp = data.get("courses", [])
      courses = courses + [course["id"] for course in temp]
      courseTitle = courseTitle | {course["id"]: course["name"] for course in temp}

    result = {}
    today = date.today()
    start_of_curr_week = today - timedelta(days=today.weekday())
    start_of_next_week = start_of_curr_week + timedelta(days=14)
    for course in courses:
      url = f"{BASE}/courses/{course}/courseWork"
      response = await gcall(url, access_token)
      if response:
          result[courseTitle[course]] = []
          subs = await list_submissions(course, access_token)
          state_by_work = {s["courseWorkId"]: s["state"] for s in subs}
          courseWork = response["courseWork"]
  
          for work in courseWork:
              state = state_by_work.get(work["id"])
              if state in ("NEW", "CREATED", "RECLAIMED_BY_STUDENT"):
                  dueDate = work.get("dueDate")
                  if dueDate:
                      s = f"{dueDate["year"]}-{dueDate["month"]}-{dueDate["day"]}"
                      temp_date = datetime.strptime(s, "%Y-%m-%d").date()
                      if temp_date >= start_of_curr_week and temp_date <= start_of_next_week:
                        result[courseTitle[course]].append(f"TO DO: {work["title"]} Due date on {calendar.month_name[dueDate["month"]]} {dueDate["day"]} {dueDate["year"]}")
                  else:
                      result[courseTitle[course]].append(f"TO DO: {work["title"]} No Due Date")
          if not result[courseTitle[course]]:
              del result[courseTitle[course]]
    
    print(result)
    return result    
    
  except HttpError as error:
    print(f"An error occurred: {error}")



if __name__ == "__main__":
  print(classroom())
  
  
  
import json
from urllib.parse import urlencode
from js import fetch, Object
from pyodide.ffi import to_js

async def get_access_token(token_info: dict) -> str:
    resp = await fetch(
        token_info.get("token_uri", "https://oauth2.googleapis.com/token"),
        _opts(
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urlencode({
                "client_id": token_info["client_id"],
                "client_secret": token_info["client_secret"],
                "refresh_token": token_info["refresh_token"],
                "grant_type": "refresh_token",
            }),
        ),
    )
    data = json.loads(await resp.text())
    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")
    return data["access_token"]

def _opts(**kw):
    # convert a Python dict into a plain JS object for fetch
    return to_js(kw, dict_converter=Object.fromEntries)

async def gcall(url: str, access_token: str) -> dict:
    resp = await fetch(url, _opts(headers={"Authorization": f"Bearer {access_token}"}))
    text = await resp.text()
    return json.loads(text)
  
async def list_submissions(course_id: str, access_token: str) -> list:
    params = urlencode({"userId": "me", "pageSize": 100})
    url = f"{BASE}/courses/{course_id}/courseWork/-/studentSubmissions?{params}"
    data = await gcall(url, access_token)
    return data.get("studentSubmissions", [])