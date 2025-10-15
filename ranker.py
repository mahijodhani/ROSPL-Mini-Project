from datetime import datetime, timezone

class Ranker:
    def __init__(self, indexer):
        self.indexer = indexer

    def rank(self, events, query=None):
        def score(ev):
            # Handle missing or malformed date
            try:
                pub_time = datetime.strptime(ev.get("published_at", ""), "%Y-%m-%dT%H:%M:%SZ")
                pub_time = pub_time.replace(tzinfo=timezone.utc)
            except Exception:
                pub_time = datetime.now(timezone.utc)

            # More recent events get higher score
            recency_score = (datetime.now(timezone.utc) - pub_time).total_seconds()
            recency_score = max(1, 1_000_000 - recency_score)

            # Optional: add query-based boost
            query_score = 0
            if query:
                for word in query.lower().split():
                    if word in (ev.get("title") or "").lower() or word in (ev.get("description") or "").lower():
                        query_score += 500

            return query_score + recency_score

        # Sort descending (highest score = most relevant/recent)
        return sorted(events, key=score, reverse=True)