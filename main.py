import os
import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get API keys from .env
canvas_token = os.getenv("CANVAS_API_TOKEN")
##openai.api_key = os.getenv("OPENAI_API_KEY")

# Canvas domain
canvas_url = "https://sjsu.instructure.com"

# Headers for Canvas API requests
headers = {
    "Authorization": f"Bearer {canvas_token}"
}

# Get list of courses
def get_courses():
    url = f"{canvas_url}/api/v1/courses"
    params = {
        "enrollment_state": "active",        # Only active enrollments
        "include[]": "syllabus_body",        # Include syllabus
        "per_page": 100,                     # Show more results
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Error fetching courses:", response.text)
        return []
    return response.json()

# Get syllabus HTML for a course
def get_syllabus(course_id):
    url = f"{canvas_url}/api/v1/courses/{course_id}?include[]=syllabus_body"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get syllabus for course {course_id}")
        return ""
    data = response.json()
    return data.get("syllabus_body", "")

# Clean HTML content using BeautifulSoup
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator="\n")

# Extract exam dates using GPT
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

# Main execution
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
    print(cleaned_text[:1000])  # Just a preview

    print("\n--- Extracting Exam Dates... ---\n")
    exam_info = extract_exam_dates_from_text(cleaned_text)
    print("🧠 Extracted Exam Dates:")
    print(exam_info)
