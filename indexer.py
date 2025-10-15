from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class Indexer:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.events = None

    def build_index(self, events):
        """Build a TF-IDF index from event titles, descriptions, and categories"""
        self.events = events
        # Include category in the corpus for better matching
        corpus = [f"{ev['title']} {ev['description']} {ev.get('category', '')}".lower() 
                  for ev in events]
        self.vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        return self.tfidf_matrix

    def search(self, query, top_k=10):
        """Return top_k matching events using cosine similarity"""
        if self.vectorizer is None or self.tfidf_matrix is None:
            raise ValueError("Index not built yet. Call build_index first.")

        query_vec = self.vectorizer.transform([query.lower()])
        cosine_similarities = (self.tfidf_matrix @ query_vec.T).toarray().ravel()

        # Get indices of top_k results (even if score is 0)
        top_indices = np.argsort(cosine_similarities)[::-1][:top_k]
        
        # First try to get results with score > 0
        results = [
            {
                **self.events[i],
                "score": float(cosine_similarities[i])
            }
            for i in top_indices if cosine_similarities[i] > 0
        ]
        
        # If no exact matches, do fuzzy keyword search including category
        if not results:
            query_words = query.lower().split()
            scored_results = []
            
            for i, event in enumerate(self.events):
                text = f"{event.get('title', '')} {event.get('description', '')}".lower()
                category = event.get('category', '').lower()
                
                # Check category match first (higher score)
                if query.lower() in category or category in query.lower():
                    scored_results.append({
                        **event,
                        "score": 0.5  # High score for category match
                    })
                # Check if any query word appears in the text
                elif any(word in text for word in query_words):
                    scored_results.append({
                        **event,
                        "score": 0.1  # Low score for keyword match
                    })
            
            # Sort by score descending
            results = sorted(scored_results, key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
