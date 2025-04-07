from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from newspaper import Article
import time

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

            print(f"\nTitle: {title}")
            print(f"Link: {article_url}")

            try:
                # Use Newspaper3k to extract the article content
                article = Article(article_url)
                article.download()
                article.parse()

                article_content = article.text if article.text else "Content not found"

                print(f"Extracted Content: {article_content[:500]}...")  # Print first 500 chars
                print("-" * 80)

            except Exception as e:
                print(f"Error extracting content: {e}")

    else:
        print("Could not find 'What's New' section.")
else:
    print("No 'What's New' link found.")

# Close WebDriver
driver.quit()
