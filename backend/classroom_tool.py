import os.path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()

CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")
TOKEN_PATH = os.getenv("TOKEN_PATH", "token_path")

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
]


def main():
  """Shows basic usage of the Classroom API.
  Prints the names of the first 10 courses the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          CREDENTIALS_PATH, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_PATH, "w") as token:
      token.write(creds.to_json())

  try:
    courses = []
    courseTitle = []
    service = build("classroom", "v1", credentials=creds)
    request = service.courses().list(studentId="me", courseStates=["ACTIVE"], pageSize=50)
    
    while request is not None:
        response = request.execute()
        courses = courses + [course["id"] for course in response.get("courses", [])]
        courseTitle = [course["name"] for course in response.get("courses", [])]
        request = service.courses().list_next(request, response)

    
    
    result = {}
    for index, course in enumerate(courses):
        response = service.courses().courseWork().list(courseId=course).execute()     
        if response:
            result[course] = []
            subs = service.courses().courseWork().studentSubmissions().list(courseId=course, courseWorkId="-",userId="me",).execute().get("studentSubmissions", [])
            state_by_work = {s["courseWorkId"]: s["state"] for s in subs}
            courseWork = response["courseWork"]
          
            for work in courseWork:
                state = state_by_work.get(work["id"])
                if state in ("NEW", "CREATED", "RECLAIMED_BY_STUDENT"):
                    result[course].append(f"TO DO: {work["title"]} {work.get("dueDate")}")
         
    return result    
    
  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()