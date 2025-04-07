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

def scrape_sec_updates():
    print("[INFO] Setting up ChromeDriver...")

    service = Service(ChromeDriverManager().install())
    options = Options()
    # 🚨 Try disabling headless mode for debugging
    # options.add_argument("--headless=new")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=service, options=options)
    print("[INFO] Navigating to SEC Press Releases page...")

    url = "https://www.sec.gov/news/pressreleases"
    driver.get(url)

    try:
        # ✅ Scroll down to ensure all content loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for dynamic content to load

        # ✅ Wait up to 20s for the table to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        print("[INFO] Page loaded successfully!")
    except Exception as e:
        print(f"[ERROR] Table did not load: {e}")
        driver.quit()
        return []

    # ✅ Parse the updated page source
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ✅ Locate table rows
    updates = []
    table = soup.find("table")
    if not table:
        print("[ERROR] No table found. Page structure may have changed.")
        driver.quit()
        return []

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

        # ✅ Convert date to ISO format
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

    driver.quit()
    return updates

if __name__ == "__main__":
    sec_updates = scrape_sec_updates()

    if sec_updates:
        print(f"\n[✅ {len(sec_updates)} SEC Press Releases Scraped Successfully!]\n")
        for update in sec_updates:  # Print ALL updates instead of just 5
            print(update)
    else:
        print("\n[❌ No updates found. Check for errors!]\n")
