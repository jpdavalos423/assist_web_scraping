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

def extract_receiving_courses(row):
    """Extracts receiving courses, handling both single courses and AND conjunctions."""
    bracket_wrapper = row.find('div', class_='bracketWrapper')
    
    if bracket_wrapper:
        # AND conjunction case: extract all courseLine elements inside bracketContent
        bracket_content = bracket_wrapper.find('div', class_='bracketContent')
        if bracket_content:
            courses = []
            for course in bracket_content.find_all('div', class_='courseLine'):
                course_number = course.find('div', class_='prefixCourseNumber').get_text(strip=True)
                course_title = course.find('div', class_='courseTitle').get_text(strip=True)
                courses.append(f"{course_number} - {course_title}")
            return courses  # Returning a list means this represents an AND condition
    
    else:
        # Single course case: directly extract courseLine
        course = row.find('div', class_='courseLine')
        if course:
            course_number = course.find('div', class_='prefixCourseNumber').get_text(strip=True)
            course_title = course.find('div', class_='courseTitle').get_text(strip=True)
            return [f"{course_number} - {course_title}"]  # Wrap in list for consistency
    
    return []  # Return empty if no courses found



def extract_sending_courses(row):
    """Extracts sending courses while correctly handling OR and nested AND groups."""

    # Check if "No Course Articulated" is present
    if row.find('p') and "No Course Articulated" in row.find('p').get_text(strip=True):
        return "Not Articulated"

    or_groups = []  # List of OR-separated course groups
    current_or_group = []  # Stores courses before an OR separator

    # Helper function to extract a course from a `courseLine`
    def extract_course(course):
        course_number = course.find('div', class_='prefixCourseNumber').get_text(strip=True)
        course_title = course.find('div', class_='courseTitle').get_text(strip=True)
        return f"{course_number} - {course_title}"

    # **Step 1: Extract AND groups (bracketWrapper)**
    for bracket in row.find_all('div', class_='bracketWrapper'):
        and_group = [extract_course(course) for course in bracket.find_all('div', class_='courseLine')]
        current_or_group.append(and_group)  # Store AND group in OR collection

        # **Check for OR separator (`standAlone`) immediately after**
        if bracket.find_next_sibling('awc-view-conjunction', class_='standAlone'):
            or_groups.append(current_or_group)
            current_or_group = []  # Reset for the next OR group

    # **Step 2: Extract standalone courses (not inside bracketWrapper)**
    for course in row.find_all('div', class_='courseLine'):
        if course.find_parent('div', class_='bracketWrapper'):  # Skip already processed AND group courses
            continue
        current_or_group.append([extract_course(course)])  # Treat single course as an AND group

        # **Check for OR separator (`standAlone`) immediately after**
        if course.find_next_sibling('awc-view-conjunction', class_='standAlone'):
            or_groups.append(current_or_group)
            current_or_group = []  # Reset for next OR group

    # **Step 3: Append last OR group if it exists**
    if current_or_group:
        or_groups.append(current_or_group)

    # **Flatten if there's only one OR group**
    return or_groups[0] if len(or_groups) == 1 else or_groups if or_groups else "Not Articulated"





def parse_articulations(html):
    """Extracts articulation agreements from the loaded HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    articulations = []

    # Find all articulation rows
    for row in soup.find_all('div', class_='articRow'):
        # Extract receiving and sending courses
        receiving = extract_receiving_courses(row.find('div', class_='rowReceiving'))
        sending = extract_sending_courses(row.find('div', class_='rowSending'))

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
            # print("DEBUG: Raw Sending Courses ->", articulation["Sending Courses"])  # Debugging step

            def format_course_list(course_list):
                """Formats AND and OR cases for CSV output."""
                if not course_list:
                    return "Not Articulated"

                if isinstance(course_list[0], list):  # OR case (list of lists)
                    return " OR ".join(["(" + " | ".join(group) + ")" for group in course_list])
                
                return " | ".join(course_list)  # AND case (flat list)

            receiving = format_course_list(articulation["Receiving Courses"])
            sending = format_course_list(articulation["Sending Courses"])
            writer.writerow([receiving, sending])

    print(f"✅ Results saved successfully:\n- {json_path}\n- {csv_path}")



def main():
    # url = input("Please enter the Assist.org URL: ")
    url = "https://assist.org/transfer/results?year=74&institution=113&agreement=117&agreementType=to&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=74%2F113%2Fto%2F117%2FMajor%2Fcc1bac07-1f2e-4bf9-8958-4285f8805b50"

    html = get_dynamic_html(url)
    articulations = parse_articulations(html)
    
    if articulations:
        # print("Articulation Agreements Found:")
        # for art in articulations:
        #     print(f"Receiving: {art['Receiving Courses']}, Sending: {art['Sending Courses']}")
        
        save_results(articulations)  # Save data
    else:
        print("❌ No articulation agreements found.")

if __name__ == "__main__":
    main()
