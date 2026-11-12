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

load_dotenv()

CREDENTIALS_PATH = getattr(env, "CREDENTIALS_PATH", None)
TOKEN_PATH = getattr(env, "TOKEN_PATH", None)


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
]


def classroom():
  """Gets the tasks that are not yet done for each course. It returns
  a dict containing the course title as a key and a list containing strings 
  describing the course work as well as the deadline
  """

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  
  token_info = json.loads(getattr(env, "TOKEN_JSON", None))   # use your actual variable name
  creds = Credentials.from_authorized_user_info(token_info, SCOPES)
  # if os.path.exists(TOKEN_PATH):
  #   creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
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
    courses = []
    courseTitle = {}
    service = build("classroom", "v1", credentials=creds)
    request = service.courses().list(studentId="me", courseStates=["ACTIVE"], pageSize=50)
    
    while request is not None:
        response = request.execute()
        courses = courses + [course["id"] for course in response.get("courses", [])]
        courseTitle = courseTitle | {course["id"]: course["name"] for course in response.get("courses", [])}
        request = service.courses().list_next(request, response)

    result = {}
    today = date.today()
    start_of_curr_week = today - timedelta(days=today.weekday())
    start_of_next_week = start_of_curr_week + timedelta(days=14)
    for course in courses:
        response = service.courses().courseWork().list(courseId=course).execute()     
        if response:
            result[courseTitle[course]] = []
            subs = service.courses().courseWork().studentSubmissions().list(courseId=course, courseWorkId="-",userId="me",).execute().get("studentSubmissions", [])
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
         
    return result    
    
  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  print(classroom())