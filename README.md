# Real-Time Event Detection & Information Retrieval System

A Flask-based web application that fetches Indian news, detects events, and provides intelligent search using Vector Space Model (TF-IDF + Cosine Similarity).

## Features

### 🔍 Information Retrieval
- **Vector Space Model**: TF-IDF vectorization with cosine similarity ranking
- **Smart Search**: Automatic fallback to keyword matching
- **Fresh Document Fetching**: Option to fetch new documents from API for specific queries
- **Real-time Search**: Auto-search as you type (debounced)

### 📰 News Fetching
- **GNews API Integration**: Fetches up to 50 Indian news articles
- **Multi-Category**: Business, Technology, Sports, Entertainment, General
- **Query-Specific Search**: Fetch fresh documents for targeted topics

### 🏷️ Event Detection
- **Automatic Categorization**: Classifies news into 7 categories
  - Politics
  - Sports
  - Technology
  - Business
  - Economy
  - Health
  - Entertainment

### 📊 Evaluation Metrics
- **Precision**: Fraction of retrieved documents that are relevant
- **Recall**: Fraction of relevant documents that are retrieved
- **F1 Score**: Harmonic mean of precision and recall
- **Accuracy**: Overall correctness
- **MAP (Mean Average Precision)**: Quality across multiple queries

## Installation

1. **Install Dependencies**:
```bash
pip install Flask requests scikit-learn numpy
```

2. **Get GNews API Key**:
   - Visit https://gnews.io/
   - Sign up for free (100 requests/day)
   - Copy your API key

3. **Update API Key** in `app.py`:
```python
API_KEY = "your_gnews_api_key_here"
```

## Usage

### Start the Server
```bash
python app.py
```
Visit: http://localhost:5000

### Web Interface

#### 1. **Refresh All** (🔄)
- Fetches latest 50 Indian news articles
- Builds TF-IDF index
- Categorizes all articles

#### 2. **Search** (🔍)
- **Normal Search**: Searches in already fetched documents
- **Fresh Search**: Check the checkbox to fetch new documents from API
  - Example: Search "health" with checkbox enabled → fetches 50 health-related articles

#### 3. **Evaluate System** (📊)
- Tests search quality on actual fetched news
- Shows precision, recall, F1, accuracy, MAP
- Per-category breakdown
- Click **✖ Close** to dismiss results

### Command Line Evaluation
```bash
python run_evaluation.py
```
Results saved to `evaluation_results.txt`

## API Endpoints

### GET `/`
Returns the main web interface

### GET `/events`
Fetches and indexes latest Indian news
- **Returns**: Array of categorized news articles

### GET `/search?q=<query>&fetch_fresh=<true|false>`
Search for documents
- **Parameters**:
  - `q`: Search query (required)
  - `fetch_fresh`: If true, fetches new documents from API (optional, default: false)
- **Returns**: Array of ranked results with relevance scores

### GET `/evaluate`
Evaluates the IR system
- **Returns**: Precision, recall, F1, accuracy, MAP metrics

## How It Works

### Vector Space Model
1. **Document Vectorization**: Each article's title + description → TF-IDF vector
2. **Query Vectorization**: Search query → TF-IDF vector in same space
3. **Similarity Calculation**: Cosine similarity between query and all documents
4. **Ranking**: Sort by similarity score (descending)

### Evaluation
- Uses actual article categories as ground truth
- For each category (e.g., "Business"):
  - Searches for that category name
  - Compares retrieved results vs actual articles in that category
  - Calculates metrics

### Fresh Document Fetching
When checkbox is enabled:
1. Sends query to GNews search API
2. Fetches up to 50 articles matching the query
3. Builds temporary TF-IDF index
4. Returns ranked results

## File Structure

```
irs_ca/
├── app.py                  # Flask application & API endpoints
├── news_fetcher.py         # GNews API integration
├── event_detector.py       # Category classification
├── indexer.py              # TF-IDF indexing & search
├── ranker.py               # Result ranking (legacy)
├── evaluator.py            # Evaluation metrics
├── test_data.py            # Test queries (not used in current version)
├── run_evaluation.py       # Standalone evaluation script
├── templates/
│   └── index.html          # Web interface
└── README.md               # This file
```

## Configuration

### GNews API Limits (Free Tier)
- 100 requests per day
- 10 articles per request for top-headlines
- 50 articles per request for search

### Adjustable Parameters

In `app.py`:
```python
top_k=50  # Number of search results to return
```

In `news_fetcher.py`:
```python
max=50    # Max articles per API request
```

In `indexer.py`:
```python
stop_words='english'  # TF-IDF stop words
```

## Tips

1. **Better Search Results**: Enable "Fetch fresh documents" for specific topics
2. **API Limits**: Use cached search (checkbox off) to save API calls
3. **Evaluation**: Run after fetching news to see system performance
4. **Categories**: System automatically detects 7+ categories

## Troubleshooting

### No documents found
- Check API key is valid
- Verify internet connection
- Check GNews API quota (100/day)

### Search returns no results
- Try enabling "Fetch fresh documents"
- Use broader search terms
- Click "Refresh All" to fetch new articles

### Low evaluation scores
- Normal for small datasets
- Fetch more diverse articles
- Categories depend on keyword matching

## Future Enhancements

- [ ] User feedback for relevance
- [ ] Query expansion
- [ ] BM25 ranking algorithm
- [ ] Personalized recommendations
- [ ] Export search results
- [ ] Advanced filters (date, source, category)

## License

Educational project - Free to use and modify

## Author

Information Retrieval System Project
