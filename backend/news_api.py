from newsapi import NewsApiClient
from newspaper import Article
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import time
import csv

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key='3a87b64f6e85453cb9491b87db1ee95c')  # Replace with your key

# Date range
to_date = datetime.today()
from_date = to_date - timedelta(days=29)
from_date_str = from_date.strftime('%Y-%m-%d')
to_date_str = to_date.strftime('%Y-%m-%d')

# Query
query = 'regulatory compliance OR GDPR OR SEC OR RBI OR OECD'
language = 'en'

# Fetch articles
articles = newsapi.get_everything(
    q=query,
    language=language,
    from_param=from_date_str,
    to=to_date_str,
    sort_by='publishedAt',
    page_size=20
)

# Fallback method
def fetch_fallback_article_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ' '.join(p.get_text() for p in paragraphs)
            return content.strip()
        else:
            return f"Error {response.status_code} - Cannot fetch"
    except Exception as e:
        return f"Fallback error: {e}"

# CSV output fields (same as MongoDB structure)
csv_columns = [
    "_id", "title", "link", "date", "source", "regulatory_body", "release_no",
    "content", "full_content", "categories", "impact_areas",
    "geographic_scope", "summary", "processed", "last_updated"
]

data = []

# Parse and prepare rows
for i, article in enumerate(articles['articles']):
    title = article['title']
    url = article['url']
    published_date = article.get('publishedAt', datetime.utcnow().isoformat())

    print(f"Processing: {title}")

    try:
        news_article = Article(url)
        news_article.download()
        news_article.parse()
        full_content = news_article.text.strip()

        if len(full_content) < 200:
            print("Using fallback (short content)...")
            full_content = fetch_fallback_article_text(url)
    except Exception as e:
        print(f"newspaper3k error: {e}")
        print("Using fallback method...")
        full_content = fetch_fallback_article_text(url)

    content_preview = full_content[:500]

    row = {
        "_id": f"newsapi_{i}",  # Fake unique ID for reference
        "title": title,
        "link": url,
        "date": published_date,
        "source": "NewsAPI",
        "regulatory_body": None,
        "release_no": None,
        "content": content_preview,
        "full_content": full_content,
        "categories": "Regulatory News",
        "impact_areas": "Global Compliance",
        "geographic_scope": "Global",
        "summary": None,
        "processed": False,
        "last_updated": datetime.utcnow().isoformat()
    }

    data.append(row)
    time.sleep(1)

# Write to CSV
csv_file = "newsapi_regulations.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_columns)
    writer.writeheader()
    writer.writerows(data)

print(f"\n✅ Saved {len(data)} NewsAPI articles to {csv_file}")
