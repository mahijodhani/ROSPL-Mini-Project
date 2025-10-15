import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

class Evaluator:
    """
    Evaluate Information Retrieval system using standard metrics:
    - Precision: What fraction of retrieved documents are relevant?
    - Recall: What fraction of relevant documents are retrieved?
    - F1 Score: Harmonic mean of precision and recall
    - Accuracy: Overall correctness (for binary classification)
    - Mean Average Precision (MAP): Average precision across queries
    """
    
    def __init__(self):
        self.results = []
    
    def evaluate_query(self, retrieved_docs, relevant_docs, k=10):
        """
        Evaluate a single query
        
        Args:
            retrieved_docs: List of document IDs returned by the system (top-k)
            relevant_docs: List of document IDs that are actually relevant (ground truth)
            k: Number of top results to consider
        
        Returns:
            dict with precision, recall, f1, accuracy
        """
        retrieved_docs = retrieved_docs[:k]
        
        # True Positives: Retrieved AND Relevant
        tp = len(set(retrieved_docs) & set(relevant_docs))
        
        # False Positives: Retrieved but NOT Relevant
        fp = len(set(retrieved_docs) - set(relevant_docs))
        
        # False Negatives: Relevant but NOT Retrieved
        fn = len(set(relevant_docs) - set(retrieved_docs))
        
        # True Negatives: Not retrieved and not relevant (hard to define in IR)
        # For simplicity, we'll use a fixed total document count
        
        # Precision: TP / (TP + FP)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # Recall: TP / (TP + FN)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # F1 Score: Harmonic mean of precision and recall
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Accuracy (simplified for IR context)
        # Accuracy = (TP + TN) / (TP + TN + FP + FN)
        # In IR, we focus more on precision/recall, but we can calculate it
        total_relevant = len(relevant_docs)
        accuracy = tp / total_relevant if total_relevant > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'accuracy': accuracy,
            'tp': tp,
            'fp': fp,
            'fn': fn
        }
    
    def precision_at_k(self, retrieved_docs, relevant_docs, k=10):
        """Calculate Precision@K"""
        retrieved_k = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        tp = len(retrieved_k & relevant_set)
        return tp / k if k > 0 else 0.0
    
    def recall_at_k(self, retrieved_docs, relevant_docs, k=10):
        """Calculate Recall@K"""
        retrieved_k = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        tp = len(retrieved_k & relevant_set)
        return tp / len(relevant_set) if len(relevant_set) > 0 else 0.0
    
    def average_precision(self, retrieved_docs, relevant_docs):
        """
        Calculate Average Precision (AP) for a single query
        AP = (sum of P@k for each relevant doc) / total relevant docs
        """
        if not relevant_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        precisions = []
        num_relevant_found = 0
        
        for i, doc in enumerate(retrieved_docs, 1):
            if doc in relevant_set:
                num_relevant_found += 1
                precision_at_i = num_relevant_found / i
                precisions.append(precision_at_i)
        
        return sum(precisions) / len(relevant_docs) if precisions else 0.0
    
    def mean_average_precision(self, query_results):
        """
        Calculate Mean Average Precision (MAP) across multiple queries
        
        Args:
            query_results: List of tuples [(retrieved_docs, relevant_docs), ...]
        
        Returns:
            float: MAP score
        """
        aps = [self.average_precision(retrieved, relevant) 
               for retrieved, relevant in query_results]
        return sum(aps) / len(aps) if aps else 0.0
    
    def evaluate_system(self, test_queries):
        """
        Evaluate the entire IR system with multiple test queries
        
        Args:
            test_queries: List of dicts with 'query', 'retrieved', 'relevant'
        
        Returns:
            dict with average metrics across all queries
        """
        all_metrics = []
        
        for test in test_queries:
            metrics = self.evaluate_query(
                test['retrieved'], 
                test['relevant'], 
                k=test.get('k', 10)
            )
            metrics['query'] = test['query']
            all_metrics.append(metrics)
        
        # Calculate averages
        avg_precision = np.mean([m['precision'] for m in all_metrics])
        avg_recall = np.mean([m['recall'] for m in all_metrics])
        avg_f1 = np.mean([m['f1'] for m in all_metrics])
        avg_accuracy = np.mean([m['accuracy'] for m in all_metrics])
        
        # Calculate MAP
        query_results = [(test['retrieved'], test['relevant']) for test in test_queries]
        map_score = self.mean_average_precision(query_results)
        
        return {
            'average_precision': avg_precision,
            'average_recall': avg_recall,
            'average_f1': avg_f1,
            'average_accuracy': avg_accuracy,
            'map': map_score,
            'per_query_metrics': all_metrics
        }
    
    def print_evaluation_report(self, results):
        """Print a formatted evaluation report"""
        print("\n" + "="*60)
        print("INFORMATION RETRIEVAL SYSTEM EVALUATION")
        print("="*60)
        
        print(f"\n📊 Overall Metrics:")
        print(f"  Average Precision: {results['average_precision']:.4f}")
        print(f"  Average Recall:    {results['average_recall']:.4f}")
        print(f"  Average F1 Score:  {results['average_f1']:.4f}")
        print(f"  Average Accuracy:  {results['average_accuracy']:.4f}")
        print(f"  MAP (Mean Avg Precision): {results['map']:.4f}")
        
        print(f"\n📝 Per-Query Results:")
        print("-" * 60)
        for metric in results['per_query_metrics']:
            print(f"\nQuery: '{metric['query']}'")
            print(f"  Precision: {metric['precision']:.4f} | Recall: {metric['recall']:.4f}")
            print(f"  F1 Score:  {metric['f1']:.4f} | Accuracy: {metric['accuracy']:.4f}")
            print(f"  TP: {metric['tp']}, FP: {metric['fp']}, FN: {metric['fn']}")
        
        print("\n" + "="*60)
