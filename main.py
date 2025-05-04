import os
import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

#load environment variables from .env
load_dotenv()

#get API keys from .env
canvas_token = os.getenv("CANVAS_API_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

#canvas domain
canvas_url = "https://sjsu.instructure.com"

#headers for Canvas API requests
headers = {
    "Authorization": f"Bearer {canvas_token}"
}

# Get list of courses
def get_courses():
    url = f"{canvas_url}/api/v1/courses"
    response = requests.get(url, headers=headers)
    print("DEBUG status code:", response.status_code)
    if response.status_code != 200:
        print("Error response:", response.text)
        return []
    return response.json()

#get syllabus HTML for a course
def get_syllabus(course_id):
    url = f"{canvas_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get syllabus for course {course_id}")
        return ""
    data = response.json()
    return data.get("syllabus_body", "")

#clean HTML content using BeautifulSoup
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text()

#extract exam dates using GPT
def extract_exam_dates_from_text(text):
    prompt = f"""
Read the following syllabus content and extract all test-related events (quizzes, midterms, finals, exams).
Return a JSON list like this:
[{{"type": "Midterm", "date": "YYYY-MM-DD", "time": "HH:MM"}}]

Syllabus:
{text}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("OpenAI API error:", e)
        return "[]"

#main execution
if __name__ == "__main__":
    courses = get_courses()

    for course in courses:
        if isinstance(course, dict) and 'name' in course:
            print(f"\n📘 {course['name']}")
            syllabus_html = get_syllabus(course['id'])

            if not syllabus_html:
                print("No syllabus found.")
                continue

            cleaned_text = clean_html(syllabus_html)
            exam_info = extract_exam_dates_from_text(cleaned_text)

            print("🧠 Extracted Exam Dates:")
            print(exam_info)
