import re

class EventDetector:
    def __init__(self):
        # Broader keyword-based categories
        self.categories = {
            "Politics": [
                "election", "government", "minister", "president", "parliament",
                "vote", "policy", "congress", "bjp", "aap", "senate", "political"
            ],
            "Sports": [
                "match", "tournament", "goal", "player", "team", "win", "defeat",
                "cricket", "football", "tennis", "olympic", "sports", "fifa"
            ],
            "Technology": [
                "ai", "artificial intelligence", "tech", "technology", "gadget",
                "software", "hardware", "startup", "app", "robot", "machine learning"
            ],
            "Disaster": [
                "earthquake", "flood", "storm", "cyclone", "fire", "landslide",
                "disaster", "tsunami", "explosion", "accident"
            ],
            "Business": [
                "business", "company", "corporate", "ceo", "startup", "entrepreneur",
                "merger", "acquisition", "revenue", "profit", "loss", "shares"
            ],
            "Economy": [
                "market", "stock", "economy", "finance", "bank", "inflation",
                "investment", "gdp", "rupee", "dollar"
            ],
            "Health": [
                "covid", "vaccine", "virus", "health", "hospital", "doctor",
                "disease", "infection", "medicine"
            ],
            "Entertainment": [
                "movie", "film", "actor", "actress", "bollywood", "hollywood",
                "song", "music", "celebrity", "show"
            ]
        }

    def detect_events(self, articles):
        events = []
        for art in articles:
            text = f"{art.get('title', '')} {art.get('description', '')}".lower()
            category = self.categorize(text)
            art["category"] = category
            events.append(art)
        print(f"✅ Detected {len(events)} events")
        return events

    def categorize(self, text):
        for cat, keywords in self.categories.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw.lower())}\b", text):
                    return cat
        return "General"
