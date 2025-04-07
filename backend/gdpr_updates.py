from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Selenium WebDriver setup
options = Options()
# REMOVE HEADLESS FOR DEBUGGING
# options.add_argument("--headless")  

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the GDPR News page
main_url = "https://gdpr.eu/category/news-updates/"
driver.get(main_url)
time.sleep(5)  # Wait for the page to load fully

# Debugging Step 1: Check if page loaded
print("Page loaded successfully!")

# Extract articles
try:
    articles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "post"))
    )
    print(f"Found {len(articles)} articles!")  # Debugging step
except Exception as e:
    print("Failed to find articles:", e)
    driver.quit()
    exit()

# List to store extracted data
data = []

for idx in range(len(articles)):  # Iterate by index to avoid stale elements
    try:
        # Re-find elements before accessing them
        articles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "post"))
        )
        article = articles[idx]

        title_element = article.find_element(By.TAG_NAME, "h4").find_element(By.TAG_NAME, "a")
        title = title_element.text
        link = title_element.get_attribute("href")

        summary = article.find_element(By.TAG_NAME, "p").text
        date = article.find_element(By.CLASS_NAME, "post-date").text

        print(f"\n{idx+1}. Extracting: {title} ({link})")

        # Open article page
        driver.get(link)
        time.sleep(5)  # Wait for page to load

        # Extract article content
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        full_content = "\n".join([p.text for p in paragraphs])

        # Store extracted data
        data.append({
            "title": title,
            "link": link,
            "date": date,
            "summary": summary,
            "content": full_content
        })

        print(f"Extracted {len(paragraphs)} paragraphs for '{title}'")

        # Go back to main page
        driver.get(main_url)
        time.sleep(3)

    except Exception as e:
        print(f"Error extracting article {idx+1}: {e}")

# Close browser
driver.quit()

# Print extracted articles
for idx, article in enumerate(data, start=1):
    print(f"\n{idx}. {article['title']}")
    print(f"   URL: {article['link']}")
    print(f"   Date: {article['date']}")
    print(f"   Summary: {article['summary']}")
    print(f"\n   Full Article Content:\n{article['content'][:1000]}...")  # Show only first 500 chars
    print("="*100)
