from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import pymongo
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import os

# Import MongoDB config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:28017/")
DB_NAME = "regulatory_ai"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
regulations_collection = db["regulatory_updates"]

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the UNEP page
url = "https://www.unep.org/resources/filter/page=0/langcode=en/sort_by=publication_date/sort_order=desc/type=press_release,resource,report_flagship,technical_highlight,landing_page,our_work,regional_program_activity_work,page,feature_portal,stub_content"
driver.get(url)
time.sleep(5)  # Allow time for page to load

articles = []

# Function to scrape articles from the current page
def scrape_articles():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for article in soup.find_all("a", href=True):
        if "/news-and-stories/" in article["href"]:  # Filter valid article links
            title = article.text.strip()
            link = "https://www.unep.org" + article["href"]  # Convert to full URL
            
            # Extract summary (from <div> right after <a>)
            summary_tag = article.find_next("div")
            summary = summary_tag.text.strip() if summary_tag else "No summary available"
            
            # Create document in required format
            document = {
                "title": title,
                "link": link,
                "date": datetime.utcnow().isoformat(),  # Use current date in ISO format
                "source": "UNEP",
                "regulatory_body": "United Nations Environment Programme",
                "release_no": None,  # No release number available
                "content": summary[:500],  # First 500 characters of summary
                "full_content": summary,  # Full summary as content
                "categories": ["Environmental Regulations", "Sustainability"],
                "impact_areas": ["Global Climate", "Environmental Policy"],
                "geographic_scope": "Global",
                "summary": summary,
                "processed": False,
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Save to MongoDB
            regulations_collection.insert_one(document)
            articles.append(document)

# Keep clicking "Next" until we get 20 articles
while len(articles) < 20:
    scrape_articles()
    
    try:
        # Find the "Next" button
        next_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Next')]")
        driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Scroll to it
        time.sleep(1)  # Give time for UI update
        next_button.click()  # Click Next
        time.sleep(5)  # Wait for new page to load
    except NoSuchElementException:
        print("No more 'Next' button found. Stopping...")
        break  # Stop if there's no "Next" button

# Close WebDriver
driver.quit()

print(f"✅ Scraped {len(articles)} articles and stored in MongoDB!")
