import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
canvas_token = os.getenv("CANVAS_API_TOKEN")
canvas_url = "https://sjsu.instructure.com"
SCOPES = ['https://www.googleapis.com/auth/calendar']

headers = {
    "Authorization": f"Bearer {canvas_token}"
}

#canvas functions
def get_courses():
    url = f"{canvas_url}/api/v1/courses"
    params = {
        "enrollment_state": "active",
        "include[]": "syllabus_body",
        "per_page": 100,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Error fetching courses:", response.text)
        return []
    return response.json()

def get_syllabus(course_id):
    url = f"{canvas_url}/api/v1/courses/{course_id}?include[]=syllabus_body"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get syllabus for course {course_id}")
        return ""
    return response.json().get("syllabus_body", "")

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator="\n")

#openai functions

def extract_exam_dates_from_text(text):
    prompt = f"""
Read the following syllabus content and extract all test-related events (quizzes, midterms, finals, exams).
Return a JSON list like this:
[{{"type": "Midterm", "date": "YYYY-MM-DD", "time": "HH:MM"}}]

Syllabus:
{text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("OpenAI API error:", e)
        return []

#gcal functions
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_event(service, exam_type, date, time=None):
    if time:
        start_datetime = f"{date}T{time}:00"
        event = {
            'summary': f"{exam_type}",
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/Los_Angeles'  # Change this to your timezone if needed
            },
            'end': {
                'dateTime': start_datetime,
                'timeZone': 'America/Los_Angeles'
            }
        }
    else:
        event = {
            'summary': f"{exam_type}",
            'start': {'date': date},
            'end': {'date': date}
        }

    try:
        service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Added to calendar: {exam_type} on {date} {time or ''}")
    except Exception as e:
        print(f"❌ Failed to add event: {e}")

#main
if __name__ == "__main__":
    courses = get_courses()
    courses = [c for c in courses if 'name' in c and 'id' in c]

    if not courses:
        print("No valid courses found.")
        exit()

    print("Available Courses:")
    for idx, course in enumerate(courses):
        print(f"{idx+1}. {course['name']}")

    try:
        selected_idx = int(input("Select a course by number: ")) - 1
        selected_course = courses[selected_idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        exit()

    syllabus_html = get_syllabus(selected_course['id'])
    if not syllabus_html:
        print("No syllabus found for this course.")
        exit()

    print("\n--- Syllabus Preview (cleaned text) ---\n")
    cleaned_text = clean_html(syllabus_html)
    print(cleaned_text[:1000])

    print("\n--- Extracting Exam Dates... ---\n")
    exams = extract_exam_dates_from_text(cleaned_text)

    if not exams:
        print("No exam dates found.")
        exit()

    print("🧠 Extracted Exam Dates:")
    for exam in exams:
        print(exam)

    print("\n--- Adding to Google Calendar... ---\n")
    calendar_service = authenticate_google_calendar()

    for exam in exams:
        exam_type = exam.get("type", "Exam")
        date = exam.get("date")
        time = exam.get("time", None)
        if date:
            add_event(calendar_service, exam_type, date, time)
