"""
Standalone script to evaluate the IR system
Run this after fetching news to see evaluation metrics
"""

from news_fetcher import NewsFetcher
from event_detector import EventDetector
from indexer import Indexer
from evaluator import Evaluator

def main():
    # API Key
    API_KEY = "f013b10cf5a2cf8c3ba94d8a51e8537b"
    
    print("🔄 Fetching news articles...")
    news_fetcher = NewsFetcher(API_KEY)
    raw_news = news_fetcher.fetch_news()
    parsed_news = news_fetcher.parse_news(raw_news)
    
    if not parsed_news:
        print("❌ No articles found!")
        return
    
    print("🔍 Detecting events...")
    event_detector = EventDetector()
    events = event_detector.detect_events(parsed_news)
    
    print("📚 Building TF-IDF index...")
    indexer = Indexer()
    indexer.build_index(events)
    
    print("\n🧪 Running evaluation on actual fetched news...")
    evaluator = Evaluator()
    test_results = []
    
    # Use actual categories from fetched news as test queries
    categories = set(event.get('category', 'General') for event in events)
    print(f"  Found categories: {', '.join(categories)}")
    
    # Run evaluation for each category
    for category in categories:
        if category == 'General':
            continue  # Skip generic category
        
        query = category.lower()
        print(f"  Testing query: '{query}'")
        
        # Get retrieved documents from our system
        retrieved_results = indexer.search(query, top_k=50)
        retrieved_indices = []
        for r in retrieved_results:
            for i, event in enumerate(indexer.events):
                if (event.get('title') == r.get('title') and 
                    event.get('url') == r.get('url')):
                    retrieved_indices.append(i)
                    break
        
        # Ground truth: all documents that actually belong to this category
        relevant_indices = [i for i, event in enumerate(indexer.events) 
                           if event.get('category') == category]
        
        print(f"    Retrieved: {len(retrieved_indices)}, Relevant: {len(relevant_indices)}")
        
        if relevant_indices:
            test_results.append({
                'query': query,
                'retrieved': retrieved_indices,
                'relevant': relevant_indices,
                'k': 10
            })
    
    # Evaluate the system
    print("\n📊 Calculating metrics...")
    evaluation_results = evaluator.evaluate_system(test_results)
    
    # Print detailed report
    evaluator.print_evaluation_report(evaluation_results)
    
    # Save results to file
    print("\n💾 Saving results to evaluation_results.txt...")
    with open('evaluation_results.txt', 'w') as f:
        f.write("INFORMATION RETRIEVAL SYSTEM EVALUATION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Average Precision: {evaluation_results['average_precision']:.4f}\n")
        f.write(f"Average Recall:    {evaluation_results['average_recall']:.4f}\n")
        f.write(f"Average F1 Score:  {evaluation_results['average_f1']:.4f}\n")
        f.write(f"Average Accuracy:  {evaluation_results['average_accuracy']:.4f}\n")
        f.write(f"MAP:               {evaluation_results['map']:.4f}\n\n")
        
        f.write("Per-Query Results:\n")
        f.write("-"*60 + "\n")
        for metric in evaluation_results['per_query_metrics']:
            f.write(f"\nQuery: '{metric['query']}'\n")
            f.write(f"  Precision: {metric['precision']:.4f}\n")
            f.write(f"  Recall:    {metric['recall']:.4f}\n")
            f.write(f"  F1 Score:  {metric['f1']:.4f}\n")
            f.write(f"  Accuracy:  {metric['accuracy']:.4f}\n")
            f.write(f"  TP: {metric['tp']}, FP: {metric['fp']}, FN: {metric['fn']}\n")
    
    print("✅ Results saved to evaluation_results.txt")

if __name__ == '__main__':
    main()
