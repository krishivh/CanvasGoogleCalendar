import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://canvas.instructure.com/api/v1"
TOKEN = os.getenv("CANVAS_API_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def get_courses():
    """Fetch all courses for the authenticated Canvas user."""
    response = requests.get(f"{API_URL}/courses", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_syllabus(course_id):
    """Fetch the syllabus body for a specific course by ID."""
    response = requests.get(
        f"{API_URL}/courses/{course_id}?include[]=syllabus_body", headers=HEADERS
    )
    response.raise_for_status()
    return response.json().get("syllabus_body", "")
