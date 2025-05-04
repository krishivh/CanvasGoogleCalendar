import os
from openai import OpenAI
from dotenv import load_dotenv

#load .env variables (API keys)
load_dotenv()

#initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#function to call GPT and extract exam dates
def extract_exam_dates_from_text(text):
    prompt = f"""
Read the following syllabus and extract all test-related events (quizzes, midterms, finals, exams).
Return a JSON list like this:
[{{"type": "Midterm", "date": "YYYY-MM-DD", "time": "HH:MM"}}]

Syllabus:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content

#main script
if __name__ == "__main__":
    try:
        #read the syllabus text from the file created by Selenium
        with open("syllabus_output.txt", "r") as f:
            syllabus_text = f.read()

        print("Extracting exam dates with GPT...\n")
        extracted = extract_exam_dates_from_text(syllabus_text)
        print("🧠 Extracted Exam Info:")
        print(extracted)

    except FileNotFoundError:
        print("❌ Could not find syllabus_output.txt. Make sure you've run canvas_scraper.py first.")
    except Exception as e:
        print("❌ An error occurred:", e)
