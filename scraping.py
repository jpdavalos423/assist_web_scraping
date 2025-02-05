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
    """Extracts course numbers and titles from receiving/sending rows,
    while considering 'AND' and 'OR' conjunctions."""
    courses = []

    # Look for 'AND' conjunctions
    and_courses = row.find_all('div', class_='and conjunction series')
    if and_courses:
        and_course_data = []
        for course in and_courses:
            course_number = course.get_text(strip=True)
            title = course.find_next('div', class_='courseTitle')
            if title:
                course_title = title.get_text(strip=True)
                and_course_data.append(f"{course_number} - {course_title}")
        if and_course_data:
            courses.append({"courses": and_course_data, "conjunction": "AND"})
    
    # Look for 'OR' conjunctions
    or_courses = row.find_all('div', class_='conjunction or standAlone')
    if or_courses:
        or_course_data = []
        for course in or_courses:
            course_number = course.get_text(strip=True)
            title = course.find_next('div', class_='courseTitle')
            if title:
                course_title = title.get_text(strip=True)
                or_course_data.append(f"{course_number} - {course_title}")
        if or_course_data:
            courses.append({"courses": or_course_data, "conjunction": "OR"})

    # Regular courses
    regular_courses = []
    for course in row.find_all('div', class_='prefixCourseNumber'):
        course_number = course.get_text(strip=True)
        title = course.find_next('div', class_='courseTitle')
        if title:
            course_title = title.get_text(strip=True)
            regular_courses.append(f"{course_number} - {course_title}")
    if regular_courses:
        courses.append({"courses": regular_courses, "conjunction": None})

    return courses

def parse_articulations(html):
    """Extracts articulation agreements from the loaded HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    articulations = []

    # Find all articulation rows
    for row in soup.find_all('div', class_='articRow'):
        # Extract receiving and sending courses
        receiving_courses = extract_courses(row.find('div', class_='rowReceiving'))
        sending_courses = extract_courses(row.find('div', class_='rowSending'))

        # Pair receiving courses with sending courses, include conjunctions
        articulation = {
            "Receiving Courses": receiving_courses,
            "Sending Courses": sending_courses
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
        writer.writerow(["Receiving Courses", "Receiving Conjunction", "Sending Courses", "Sending Conjunction"])  # Headers
        for articulation in articulations:
            # For Receiving Courses
            for rec in articulation["Receiving Courses"]:
                receiving = " | ".join(rec["courses"])  # Join multiple courses
                receiving_conjunction = rec["conjunction"] if rec["conjunction"] else "None"
                # For Sending Courses
                for send in articulation["Sending Courses"]:
                    sending = " | ".join(send["courses"])  # Join multiple courses
                    sending_conjunction = send["conjunction"] if send["conjunction"] else "None"
                    writer.writerow([receiving, receiving_conjunction, sending, sending_conjunction])

    print(f"✅ Results saved successfully:\n- {json_path}\n- {csv_path}")

def main():
    url = input("Please enter the URL to scrape: ")  # Prompt for the URL
    
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
