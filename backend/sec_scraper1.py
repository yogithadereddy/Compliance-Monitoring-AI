from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

def scrape_sec_updates(max_pages=5):
    print("[INFO] Setting up ChromeDriver...")

    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)
    url = "https://www.sec.gov/news/pressreleases"
    driver.get(url)
    
    updates = []
    page_count = 0

    while page_count < max_pages:
        try:
            # Wait for table to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
            print(f"[INFO] Scraping page {page_count + 1}...")

            # Parse page content
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table")

            if not table:
                print("[ERROR] No table found.")
                break

            rows = table.find_all("tr")[1:]  # Skip header row
            for row in rows:
                columns = row.find_all("td")
                if len(columns) < 3:
                    continue  # Skip invalid rows

                date_text = columns[0].text.strip()
                title_element = columns[1].find("a")
                release_no = columns[2].text.strip()

                if not title_element:
                    continue  # Skip if no title

                title = title_element.text.strip()
                link = "https://www.sec.gov" + title_element["href"]

                # Convert date to ISO format
                try:
                    date_iso = datetime.strptime(date_text, "%B %d, %Y").isoformat()
                except ValueError:
                    date_iso = None  # Handle incorrect date formats

                updates.append({
                    "source": "SEC",
                    "title": title,
                    "link": link,
                    "date": date_iso,
                    "release_no": release_no
                })

            # Check for "Next" page button
            next_button = driver.find_element(By.CSS_SELECTOR, "a.usa-pagination__next-page")
            if next_button:
                next_button.click()  # Click to go to the next page
                time.sleep(3)  # Allow time for the next page to load
                page_count += 1
            else:
                break  # No more pages to navigate
        except Exception as e:
            print(f"[ERROR] Issue navigating pages: {e}")
            break

    driver.quit()
    return updates

if __name__ == "__main__":
    sec_updates = scrape_sec_updates(max_pages=5)

    if sec_updates:
        print(f"\n[✅ {len(sec_updates)} SEC Press Releases Scraped Successfully!]\n")
        for update in sec_updates:
            print(update)
    else:
        print("\n[❌ No updates found. Check for errors!]\n")
