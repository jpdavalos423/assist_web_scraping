import os
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

def get_dynamic_html(url):
    """Uses Selenium to load JavaScript-rendered content."""
    options = Options()
    options.add_argument("--headless")  # Runs in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")  # Suppresses unnecessary logs

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load
    
    page_source = driver.page_source  # Get updated HTML
    driver.quit()
    
    return page_source

def extract_courses(row):
    """Extracts course numbers and titles from receiving/sending rows."""
    courses = []
    for course in row.find_all('div', class_='prefixCourseNumber'):
        course_number = course.get_text(strip=True)
        title = course.find_next('div', class_='courseTitle')
        if title:
            course_title = title.get_text(strip=True)
            courses.append(f"{course_number} - {course_title}")
    return courses

def parse_articulations(html):
    """Extracts articulation agreements from the loaded HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    articulations = []

    # Find all articulation rows
    for row in soup.find_all('div', class_='articRow'):
        # Extract receiving and sending courses
        receiving = extract_courses(row.find('div', class_='rowReceiving'))
        sending = extract_courses(row.find('div', class_='rowSending'))

        # Pair receiving courses with sending courses
        articulation = {
            "Receiving Courses": receiving,
            "Sending Courses": sending
        }
        articulations.append(articulation)
    
    return articulations

def save_results(articulations):
    """Saves articulation agreements in 'results/' as JSON and CSV."""
    folder_name = "results"
    os.makedirs(folder_name, exist_ok=True)  # Create folder if it doesn't exist

    # Save as JSON
    json_path = os.path.join(folder_name, "articulations.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(articulations, json_file, indent=4)

    # Save as CSV
    csv_path = os.path.join(folder_name, "articulations.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Receiving Courses", "Sending Courses"])  # Headers
        for articulation in articulations:
            receiving = " | ".join(articulation["Receiving Courses"])  # Join multiple courses
            sending = " | ".join(articulation["Sending Courses"])
            writer.writerow([receiving, sending])

    print(f"✅ Results saved successfully:\n- {json_path}\n- {csv_path}")

def main():
    url = input("Please enter the Assist.org URL: ")

    html = get_dynamic_html(url)
    articulations = parse_articulations(html)
    
    if articulations:
        print("Articulation Agreements Found:")
        for art in articulations:
            print(f"Receiving: {art['Receiving Courses']}, Sending: {art['Sending Courses']}")
        
        save_results(articulations)  # Save data
    else:
        print("❌ No articulation agreements found.")

if __name__ == "__main__":
    main()
