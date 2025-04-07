from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Selenium WebDriver with ChromeDriverManager
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Automatically install and manage ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open RBI website
driver.get("https://rbi.org.in/")

# Wait for page to load
time.sleep(3)

# Locate "What's New" section (adjust selector if needed)
whats_new_section = driver.find_element(By.ID, "whatsnew")

# Click "What's New" section to expand (if required)
driver.execute_script("arguments[0].click();", whats_new_section)

# Wait for the section to load
time.sleep(2)

# Find all article links in "What's New"
article_links = driver.find_elements(By.CSS_SELECTOR, "li a")

# Iterate through the links
for link in article_links:
    title = link.text.strip()
    url = link.get_attribute("href")

    if not url:
        continue  # Skip if no URL found

    print(f"Title: {title}")
    print(f"Link: {url}")

    # Open the link in a new tab
    driver.execute_script("window.open(arguments[0]);", url)
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for the article page to load
    time.sleep(3)

    try:
        # Extract content from the page (adjust selector as needed)
        content = driver.find_element(By.TAG_NAME, "body").text.strip()
        print(f"Content: {content[:500]}...")  # Print first 500 characters
    except:
        print("Content: Content not found.")

    print("-" * 80)

    # Close the new tab and switch back to the main page
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Close the browser
driver.quit()
