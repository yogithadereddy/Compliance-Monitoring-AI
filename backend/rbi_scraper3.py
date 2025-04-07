from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime
import time
from mongodb_config import regulations_collection  # Import MongoDB collection

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Automatically manage ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open RBI website
base_url = "https://www.rbi.org.in/"
driver.get(base_url)

# Wait for the page to load
time.sleep(3)

# Parse page source
soup = BeautifulSoup(driver.page_source, "html.parser")

# Locate "What's New" section
whats_new_section = soup.find("a", id="whatsnew")

if whats_new_section:
    parent_section = whats_new_section.find_parent()
    if parent_section:
        whats_new_list = parent_section.find_next("ul")
    else:
        whats_new_list = None

    if whats_new_list:
        news_links = whats_new_list.find_all("a", href=True)

        for link in news_links:
            title = link.text.strip()
            article_url = link["href"]

            if not article_url.startswith("http"):  # Ensure full URL
                article_url = "https://www.rbi.org.in/" + article_url

            if "More" in title or "Recruitment" in title:  
                # Skip "More" and Recruitment-related announcements
                continue

            try:
                # Use Newspaper3k to extract the article content
                article = Article(article_url)
                article.download()
                article.parse()

                if not article.text.strip():
                    continue  # Skip if no content found

                article_content = article.text  # Full content

                # ✅ Define the document structure
                document = {
                    "title": title,
                    "link": article_url,
                    "date": datetime.utcnow().isoformat(),  # Store current UTC date
                    "source": "RBI",
                    "regulatory_body": "Reserve Bank of India",
                    "release_no": None,  # No release number available
                    "content": article_content[:500],  # Short preview (first 500 chars)
                    "full_content": article_content,  # Complete content fetched
                    "categories": ["Monetary Policy", "Banking Regulations"],  # Default categories
                    "impact_areas": ["Banking Sector", "Indian Economy"],  # Default impact areas
                    "geographic_scope": "India",
                    "summary": None,
                    "processed": False,
                    "last_updated": datetime.utcnow().isoformat()
                }

                # ✅ Store the document in MongoDB
                regulations_collection.insert_one(document)
                print(f"Stored: {title}")

            except Exception as e:
                print(f"Error extracting content: {e}")

    else:
        print("Could not find 'What's New' section.")
else:
    print("No 'What's New' link found.")

# Close WebDriver
driver.quit()
