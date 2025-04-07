from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
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
    parent_section = whats_new_section.find_parent()  # Locate parent
    if parent_section:
        whats_new_list = parent_section.find_next("ul")  # Find next <ul> with links
    else:
        whats_new_list = None

    if whats_new_list:
        news_links = whats_new_list.find_all("a", href=True)

        for link in news_links:
            title = link.text.strip()
            article_url = link["href"]

            print(f"Title: {title}")
            print(f"Link: {article_url}")

            # Click the link to open the actual content
            try:
                driver.get(article_url)
                time.sleep(3)  # Allow page to load

                # Parse new page source
                article_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract content
                content_section = article_soup.find("div", class_="content")  # Adjust based on actual structure
                article_content = content_section.get_text(strip=True) if content_section else "Content not found"

                print(f"Content: {article_content[:500]}...")  # Print first 500 chars
                print("-" * 80)

            except Exception as e:
                print(f"Error extracting content: {e}")

    else:
        print("Could not find 'What's New' section.")
else:
    print("No 'What's New' link found.")

# Close WebDriver
driver.quit()
