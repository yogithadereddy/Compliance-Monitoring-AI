from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from newspaper import Article
import time
from datetime import datetime
from mongodb_config import db  # Import MongoDB connection

def scrape_sec_updates():
    print("[INFO] Setting up ChromeDriver...")

    service = Service(ChromeDriverManager().install())
    options = Options()
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
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for dynamic content to load

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        print("[INFO] Page loaded successfully!")
    except Exception as e:
        print(f"[ERROR] Table did not load: {e}")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")

    updates = []
    table = soup.find("table")
    if not table:
        print("[ERROR] No table found. Page structure may have changed.")
        driver.quit()
        return []

    rows = table.find_all("tr")[1:]
    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 3:
            continue

        date_text = columns[0].text.strip()
        title_element = columns[1].find("a")
        release_no = columns[2].text.strip()

        if not title_element:
            continue

        title = title_element.text.strip()
        link = "https://www.sec.gov" + title_element["href"]

        try:
            date_iso = datetime.strptime(date_text, "%B %d, %Y").isoformat()
        except ValueError:
            date_iso = None

        full_content = extract_article_content(link)

        document = {
            "title": title,
            "link": link,
            "date": date_iso,
            "source": "SEC",
            "regulatory_body": "Securities and Exchange Commission",
            "release_no": release_no,
            "content": full_content[:500],
            "full_content": full_content,
            "categories": ["Financial Regulations", "Investment"],
            "impact_areas": ["Investors", "US Economy"],
            "geographic_scope": "USA",
            "summary": None,
            "processed": False,
            "last_updated": datetime.utcnow().isoformat()
        }

        store_in_mongo(document)
        updates.append(document)

    driver.quit()
    return updates

def extract_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        return f"[ERROR] Failed to fetch article content: {e}"

def store_in_mongo(document):
    existing_doc = db.regulatory_updates.find_one({"release_no": document["release_no"]})
    
    if existing_doc:
        print(f"[INFO] Skipping already existing release: {document['release_no']}")
    else:
        db.regulatory_updates.insert_one(document)
        print(f"[✅] Inserted: {document['title']} ({document['release_no']})")

if __name__ == "__main__":
    sec_updates = scrape_sec_updates()

    if sec_updates:
        print(f"\n[✅ {len(sec_updates)} SEC Press Releases Scraped and Stored in MongoDB Successfully!]\n")
    else:
        print("\n[❌ No updates found. Check for errors!]\n")
