import os
import sys
import time
import traceback
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging

# where your per‐CC URL lists live:
CC_AGREEMENTS_DIR = "cc_agreements"

# where we dump the per‐CC CSVs
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_dynamic_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        # Wait up to 15 seconds for articulation rows to appear
        wait_time = 15
        start_time = time.time()
        while time.time() - start_time < wait_time:
            html = driver.page_source
            if "articRow" in html:
                return html
            time.sleep(1)
        return html
    finally:
        driver.quit()

def parse_articulations(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", class_="articRow")
    
    # Add validation for empty results
    if not rows:
        logging.warning(f"No articulation rows found in HTML. Page length: {len(html)}")
        if "No agreements were found" in html:
            logging.warning("Page indicates no agreements exist")
        elif "loading" in html.lower():
            logging.warning("Page might not have finished loading")
    
    out = []
    for row in rows:
        recv = extract_receiving_courses(row.select_one(".rowReceiving"))
        send = extract_sending_courses(row.select_one(".rowSending"))
        out.append({"Receiving": recv, "Sending": send})
    return out

def extract_receiving_courses(row):
    wrapper = row.find("div", class_="bracketWrapper")
    if wrapper:
        content = wrapper.find("div", class_="bracketContent")
        return [
            cl.find("div", class_="prefixCourseNumber").get_text(strip=True)
            for cl in content.find_all("div", class_="courseLine")
        ]
    single = row.select_one(".courseLine .prefixCourseNumber")
    return [single.get_text(strip=True)] if single else []

def extract_sending_courses(row):
    # "Not Articulated"
    if row.find("p") and "No Course Articulated" in row.get_text():
        return ["Not Articulated"]

    groups = []
    current = []

    def code_of(cl):
        return cl.find("div", class_="prefixCourseNumber").get_text(strip=True)

    # AND‑groups
    for br in row.find_all("div", class_="bracketWrapper"):
        and_list = [ code_of(cl) for cl in br.find_all("div", class_="courseLine") ]
        current.append(and_list)
        if br.find_next_sibling("awc-view-conjunction", class_="standAlone"):
            groups.append(current); current = []

    # standalone courseLines
    for cl in row.find_all("div", class_="courseLine"):
        if cl.find_parent("div", class_="bracketWrapper"):
            continue
        current.append([code_of(cl)])
        if cl.find_next_sibling("awc-view-conjunction", class_="standAlone"):
            groups.append(current); current = []

    if current:
        groups.append(current)

    # flatten if single OR‑group
    return groups[0] if len(groups)==1 else groups

def parse_articulations(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for row in soup.find_all("div", class_="articRow"):
        recv = extract_receiving_courses(row.select_one(".rowReceiving"))
        send = extract_sending_courses(row.select_one(".rowSending"))
        out.append({"Receiving": recv, "Sending": send})
    return out

def process_sending_courses(sending):
    if not sending or sending == ["Not Articulated"]:
        return ["Not Articulated"]
    # nested OR?
    if isinstance(sending[0], list):
        return ["; ".join(group) for group in sending]
    # single list
    return ["; ".join(sending)]

def find_cc_urls(cc_name):
    """
    Reads cc_agreements/{CC}/agreements.txt,
    expecting lines "University of California X: <url>".
    """
    safe = cc_name.replace(" ", "_")
    path = os.path.join(CC_AGREEMENTS_DIR, safe, "agreements.txt")
    if not os.path.exists(path):
        print(f"❌ No file at {path}")
        return []

    pairs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            uc_name, url = line.split(":", 1)
            url = url.strip()
            if url.startswith("http"):
                pairs.append((uc_name.strip(), url))
    return pairs

def write_csv(cc_name, rows):
    safe = cc_name.replace(" ", "_")
    out_path = os.path.join(RESULTS_DIR, f"{safe}_allUC.csv")

    max_groups = max(len(r["OR Groups"]) for r in rows) if rows else 0
    headers = ["UC Campus","CC","UC Course Requirement"] + [f"Courses Group {i}" for i in range(1, max_groups+1)]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rec in rows:
            base = {
                "UC Campus": rec["UC Campus"],
                "CC": cc_name,
                "UC Course Requirement": "; ".join(rec["Receiving"])
            }
            for i, grp in enumerate(rec["OR Groups"], start=1):
                base[f"Courses Group {i}"] = grp
            # ensure all headers exist
            for h in headers:
                base.setdefault(h, "")
            writer.writerow(base)

    print(f"\n✅ Overwritten → {out_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scraping.py '<Community College Name>'")
        sys.exit(1)

    cc_name = sys.argv[1].strip()
    print(f"\n🔧 Re‐scraping all UCs for: {cc_name}\n")
    logging.info(f"Starting scraping for {cc_name}")

    pairs = find_cc_urls(cc_name)
    if not pairs:
        logging.error(f"No URL pairs found for {cc_name}")
        return

    all_rows = []
    failed_ucs = []
    
    for uc_name, url in pairs:
        print(f"→ {uc_name}: {url}")
        logging.info(f"Processing {uc_name}: {url}")
        
        for attempt in range(1, 4):  # Increased to 3 attempts
            try:
                html = get_dynamic_html(url)
                arts = parse_articulations(html)
                if not arts:
                    logging.warning(f"No articulations found for {uc_name}")
                
                for a in arts:
                    all_rows.append({
                        "UC Campus": uc_name,
                        "Receiving": a["Receiving"],
                        "OR Groups": process_sending_courses(a["Sending"])
                    })
                logging.info(f"Successfully processed {uc_name} with {len(arts)} articulations")
                break
                
            except Exception as e:
                logging.error(f"Attempt {attempt} failed for {uc_name}: {str(e)}")
                print(f"  ⚠️ attempt {attempt} failed: {e}")
                traceback.print_exc(limit=1)
                time.sleep(10 * attempt)  # Increased delay between retries
        else:
            failed_ucs.append(uc_name)
            print(f"  ✗ all retries failed for {uc_name}")
            logging.error(f"All retries failed for {uc_name}")

    if failed_ucs:
        print("\n⚠️ Failed to process these UCs:")
        for uc in failed_ucs:
            print(f"  - {uc}")
        logging.error(f"Failed UCs for {cc_name}: {', '.join(failed_ucs)}")

    write_csv(cc_name, all_rows)
    logging.info(f"Completed processing {cc_name}. Total rows: {len(all_rows)}")

if __name__=="__main__":
    main()
