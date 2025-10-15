"""
Test dataset with ground truth relevance judgments for evaluation
Each test case has:
- query: search term
- relevant_categories: categories that should be considered relevant
- relevant_keywords: keywords that indicate relevance
"""

TEST_QUERIES = [
    {
        'query': 'business',
        'relevant_categories': ['Business', 'Economy'],
        'relevant_keywords': ['company', 'corporate', 'business', 'ceo', 'startup', 
                             'market', 'stock', 'economy', 'finance']
    },
    {
        'query': 'technology',
        'relevant_categories': ['Technology'],
        'relevant_keywords': ['tech', 'technology', 'ai', 'software', 'hardware', 
                             'app', 'gadget', 'robot', 'machine learning']
    },
    {
        'query': 'sports',
        'relevant_categories': ['Sports'],
        'relevant_keywords': ['cricket', 'football', 'match', 'tournament', 'player', 
                             'team', 'win', 'goal', 'sports']
    },
    {
        'query': 'politics',
        'relevant_categories': ['Politics'],
        'relevant_keywords': ['election', 'government', 'minister', 'parliament', 
                             'vote', 'policy', 'political', 'bjp', 'congress']
    },
    {
        'query': 'health',
        'relevant_categories': ['Health'],
        'relevant_keywords': ['health', 'hospital', 'doctor', 'disease', 'vaccine', 
                             'virus', 'covid', 'medicine']
    },
    {
        'query': 'entertainment',
        'relevant_categories': ['Entertainment'],
        'relevant_keywords': ['movie', 'film', 'actor', 'bollywood', 'music', 
                             'celebrity', 'show']
    }
]

def is_relevant(event, query_info):
    """
    Determine if an event is relevant to a query based on:
    1. Category match
    2. Keyword presence in title/description
    """
    # Check category
    event_category = event.get('category', 'General')
    if event_category in query_info['relevant_categories']:
        return True
    
    # Check keywords
    text = f"{event.get('title', '')} {event.get('description', '')}".lower()
    for keyword in query_info['relevant_keywords']:
        if keyword.lower() in text:
            return True
    
    return False

def get_relevant_docs(events, query_info):
    """
    Get list of relevant document indices for a query
    """
    relevant_indices = []
    for i, event in enumerate(events):
        if is_relevant(event, query_info):
            relevant_indices.append(i)
    return relevant_indices
