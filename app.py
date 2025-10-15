from flask import Flask, jsonify, render_template, request
from news_fetcher import NewsFetcher
from event_detector import EventDetector
from indexer import Indexer
from ranker import Ranker
from evaluator import Evaluator
from test_data import TEST_QUERIES, get_relevant_docs


API_KEY = "137b8c0dc9ed1be3f131d4b817570d00"  

app = Flask(__name__)

# Initialize globally so we don’t rebuild index for every request
indexer = Indexer()
ranker = None

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/events', methods=['GET'])
def get_events():
    """Fetch and index latest Indian news events"""
    news_fetcher = NewsFetcher(API_KEY)
    raw_news = news_fetcher.fetch_news()
    parsed_news = news_fetcher.parse_news(raw_news)

    if not parsed_news:
        return jsonify({"error": "No articles found"}), 404

    event_detector = EventDetector()
    events = event_detector.detect_events(parsed_news)

    # Build TF-IDF index
    tfidf_matrix = indexer.build_index(events)
    global ranker
    ranker = Ranker(indexer)

    # Return the actual events array so the frontend can display them
    return jsonify(events)

@app.route('/search', methods=['GET'])
def search_events():
    """Search events using Vector Space Model (TF-IDF + Cosine Similarity)"""
    query = request.args.get("q", "")
    fetch_fresh = request.args.get("fetch_fresh", "false").lower() == "true"
    evaluate = request.args.get("evaluate", "false").lower() == "true"
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Option 1: Fetch fresh documents from API for this specific query
    if fetch_fresh:
        print(f"🔍 Fetching fresh documents for query: '{query}'")
        news_fetcher = NewsFetcher(API_KEY)
        
        # Fetch news specifically for this query
        raw_news = news_fetcher.fetch_news_by_query(query)
        parsed_news = news_fetcher.parse_news(raw_news)
        
        if not parsed_news:
            return jsonify({"error": f"No fresh articles found for '{query}'"}), 404
        
        event_detector = EventDetector()
        fresh_events = event_detector.detect_events(parsed_news)
        
        # Build temporary index for these fresh results
        temp_indexer = Indexer()
        temp_indexer.build_index(fresh_events)
        results = temp_indexer.search(query, top_k=50)
        
        # Calculate metrics for this search if requested
        if evaluate:
            metrics = calculate_search_metrics(query, results, fresh_events)
            return jsonify({"results": results, "metrics": metrics})
        
        return jsonify(results)
    
    # Option 2: Search in existing indexed documents
    if not indexer.events:
        return jsonify({"error": "Index not ready. Click 'Refresh All' first."}), 400

    # Use indexer's search method - it handles TF-IDF + fallback to keyword search
    results = indexer.search(query, top_k=50)
    
    # Calculate metrics for this search if requested
    if evaluate:
        metrics = calculate_search_metrics(query, results, indexer.events)
        return jsonify({"results": results, "metrics": metrics})
    
    return jsonify(results)

def calculate_search_metrics(query, retrieved_results, all_events):
    """Calculate precision, recall, F1 for a single search query"""
    evaluator = Evaluator()
    
    # Get retrieved document indices
    retrieved_indices = []
    for r in retrieved_results[:10]:  # Top 10
        for i, event in enumerate(all_events):
            if (event.get('title') == r.get('title') and 
                event.get('url') == r.get('url')):
                retrieved_indices.append(i)
                break
    
    # Ground truth: Use a balanced approach
    # 1. Category match (primary)
    # 2. Strong keyword presence (secondary)
    relevant_indices = []
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Map common query terms to expected categories
    category_mapping = {
        'business': ['Business', 'Economy'],
        'economy': ['Economy', 'Business'],
        'technology': ['Technology'],
        'tech': ['Technology'],
        'sports': ['Sports'],
        'cricket': ['Sports'],
        'football': ['Sports'],
        'politics': ['Politics'],
        'political': ['Politics'],
        'health': ['Health'],
        'entertainment': ['Entertainment'],
        'movie': ['Entertainment'],
        'film': ['Entertainment']
    }
    
    # Get expected categories for this query
    expected_categories = category_mapping.get(query_lower, [])
    
    # If no mapping found, try direct category match
    if not expected_categories:
        for event in all_events:
            category = event.get('category', '')
            if query_lower in category.lower() or category.lower() in query_lower:
                expected_categories.append(category)
        expected_categories = list(set(expected_categories))
    
    # Build ground truth with scoring
    for i, event in enumerate(all_events):
        category = event.get('category', '')
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        text = f"{title} {description}"
        
        is_relevant = False
        
        # Method 1: Category match (high confidence)
        if category in expected_categories:
            is_relevant = True
        
        # Method 2: Query appears in title (high confidence)
        elif query_lower in title:
            is_relevant = True
        
        # Method 3: Multiple query words in text (medium confidence)
        elif len(query_words) > 1:
            word_count = sum(1 for word in query_words if word in text)
            if word_count >= len(query_words) * 0.5:  # At least 50% of query words
                is_relevant = True
        
        # Method 4: Single word query appears prominently (at least 2 times)
        elif len(query_words) == 1 and text.count(query_lower) >= 2:
            is_relevant = True
        
        if is_relevant:
            relevant_indices.append(i)
    
    if not relevant_indices:
        return {
            'precision': 0,
            'recall': 0,
            'f1': 0,
            'accuracy': 0,
            'total_relevant': 0,
            'total_retrieved': len(retrieved_indices),
            'note': f'No relevant documents found for query "{query}"'
        }
    
    # Calculate metrics
    metrics = evaluator.evaluate_query(retrieved_indices, relevant_indices, k=10)
    metrics['total_relevant'] = len(relevant_indices)
    metrics['total_retrieved'] = len(retrieved_indices)
    
    return metrics

@app.route('/evaluate', methods=['GET'])
def evaluate_system():
    """Evaluate the IR system using actual fetched news and their categories"""
    if not indexer.events:
        return jsonify({"error": "Index not ready. Click 'Refresh All' first."}), 400
    
    evaluator = Evaluator()
    test_results = []
    
    # Use actual categories from fetched news as test queries
    # Get unique categories from the events
    categories = set(event.get('category', 'General') for event in indexer.events)
    
    # Run evaluation for each category
    for category in categories:
        if category == 'General':
            continue  # Skip generic category
        
        query = category.lower()
        
        # Get retrieved documents from our system
        retrieved_results = indexer.search(query, top_k=50)
        retrieved_indices = []
        for r in retrieved_results:
            try:
                idx = indexer.events.index(r)
                retrieved_indices.append(idx)
            except ValueError:
                # Handle case where result might have 'score' field added
                for i, event in enumerate(indexer.events):
                    if (event.get('title') == r.get('title') and 
                        event.get('url') == r.get('url')):
                        retrieved_indices.append(i)
                        break
        
        # Ground truth: all documents that actually belong to this category
        relevant_indices = [i for i, event in enumerate(indexer.events) 
                           if event.get('category') == category]
        
        if relevant_indices:  # Only add if there are relevant docs
            test_results.append({
                'query': query,
                'retrieved': retrieved_indices,
                'relevant': relevant_indices,
                'k': 10
            })
    
    if not test_results:
        return jsonify({"error": "No categories found to evaluate"}), 400
    
    # Evaluate the system
    evaluation_results = evaluator.evaluate_system(test_results)
    
    # Print to console
    evaluator.print_evaluation_report(evaluation_results)
    
    # Return JSON response with additional info
    return jsonify({
        'total_documents': len(indexer.events),
        'categories_tested': len(test_results),
        'metrics': {
            'precision': evaluation_results['average_precision'],
            'recall': evaluation_results['average_recall'],
            'f1_score': evaluation_results['average_f1'],
            'accuracy': evaluation_results['average_accuracy'],
            'map': evaluation_results['map']
        },
        'per_query': evaluation_results['per_query_metrics']
    })

if __name__ == '__main__':
    print("🔥 Flask app with TF-IDF search is running...")
    app.run(debug=True, host="127.0.0.1", port=5000)
