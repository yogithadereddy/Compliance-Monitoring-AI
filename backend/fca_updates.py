import requests

# Replace with your actual API key from FCA
API_KEY = "your_api_key"

# FCA Handbook API endpoint (Example: Fetching latest rules and compliance notices)
API_URL = "https://www.handbook.fca.org.uk/api/v1/handbook"

# Set up headers with API key
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

# Send request to FCA API
response = requests.get(API_URL, headers=headers)

# Check response status
if response.status_code == 200:
    data = response.json()
    print("Latest FCA Handbook Rules:")
    for rule in data.get("rules", []):
        print(f"Title: {rule['title']}")
        print(f"Description: {rule['description']}")
        print(f"Link: {rule['url']}\n")
else:
    print(f"Error: Unable to fetch data. Status Code: {response.status_code}")
