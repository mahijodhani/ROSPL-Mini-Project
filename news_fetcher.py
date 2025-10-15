import requests
import datetime
import time

class NewsFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://gnews.io/api/v4"

    def fetch_news(self):
        print("📰 Fetching latest Indian news from GNews...")
        all_articles = []
        
        # GNews free tier limits to 10 articles per request
        # Fetch from multiple categories to get more diverse content
        categories = ["general", "business", "technology", "sports", "entertainment"]
        
        for category in categories:
            url = f"{self.base_url}/top-headlines?country=in&lang=en&category={category}&max=10&apikey={self.api_key}"
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    all_articles.extend(articles)
                    print(f"✅ Fetched {len(articles)} articles from {category}")
                    time.sleep(0.5)  # Small delay between requests
                else:
                    print(f"⚠️ API Error for {category}:", response.status_code, response.text)
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error for {category}:", e)
        
        print(f"✅ Total articles fetched: {len(all_articles)}")
        return {"articles": all_articles}

    def fetch_news_by_query(self, query):
        """
        Fetch news articles for a specific search query
        This allows targeted searches for specific topics
        """
        print(f"📰 Fetching news for query: '{query}'...")
        
        # GNews search endpoint - searches for specific keywords
        url = f"{self.base_url}/search?q={query}&lang=en&country=in&max=50&apikey={self.api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                print(f"✅ Fetched {len(articles)} articles for '{query}'")
                return data
            else:
                print(f"⚠️ API Error for query '{query}':", response.status_code, response.text)
                return {"articles": []}
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error for query '{query}':", e)
            return {"articles": []}

    def parse_news(self, raw):
        """Parse and normalize raw GNews API data"""
        articles = raw.get("articles", [])
        parsed = []

        for art in articles:
            title = art.get("title")
            description = art.get("description")
            if not title or not description:
                continue

            published_at = art.get("publishedAt")
            try:
                published_at = datetime.datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                ).isoformat()
            except Exception:
                published_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

            parsed.append({
                "title": title.strip(),
                "description": description.strip(),
                "url": art.get("url"),
                "source": art.get("source", {}).get("name"),
                "published_at": published_at,
                "image": art.get("image")  # GNews provides image URLs
            })

        print(f"✅ Parsed {len(parsed)} valid Indian news articles")
        return parsed

