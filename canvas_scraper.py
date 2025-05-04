from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

#launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#open Canvas login page
driver.get("https://sjsu.instructure.com")
print("👉 Please log in manually if SJSU uses SSO or Duo.")

#wait for manual login
time.sleep(30)  #adjust if needed

#go to a course with SJSU Official Syllabus
#you can copy a course link and paste it here
course_url = input("Paste the URL of a Canvas course that has the SJSU Official Syllabus: ")
driver.get(course_url)

#click the “SJSU Official Syllabus” tab
try:
    syllabus_tab = driver.find_element(By.LINK_TEXT, "SJSU Official Syllabus")
    syllabus_tab.click()
    print("✅ Navigated to SJSU Official Syllabus tab.")
except Exception as e:
    print("❌ Could not find syllabus tab:", e)

#wait for page to load
time.sleep(5)

#extract the text (or download a PDF if linked)
try:
    content = driver.find_element(By.TAG_NAME, "body").text
    print("\n📄 Syllabus Content:\n")
    print(content[:2000])  #print first 2000 characters
except Exception as e:
    print("❌ Could not extract content:", e)

#save content to file
with open("syllabus_output.txt", "w") as f:
    f.write(content)

driver.quit()
