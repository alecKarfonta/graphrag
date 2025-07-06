# Reddit Crawler for GraphRAG

A comprehensive Reddit crawling service that integrates with the GraphRAG system to extract, process, and ingest Reddit content for knowledge graph construction and analysis.

## Features

### 🚀 **Core Capabilities**
- **Multi-Modal Crawling**: Supports both Reddit API and HTTP-based scraping
- **Configurable Depth Control**: Limit comment recursion depth (1-3 levels)
- **Smart Filtering**: NSFW content filtering and quality-based post filtering
- **Auto-Integration**: Automatic ingestion into GraphRAG knowledge graph
- **Real-time Monitoring**: Live crawl progress tracking and status updates

### 🎯 **Search & Discovery**
- **Subreddit-Specific Crawling**: Target specific communities
- **Cross-Subreddit Search**: Search across all of Reddit
- **Multiple Sort Options**: Hot, top, new, relevance-based sorting
- **Time Filtering**: Hour, day, week, month, year, all-time filters
- **Query-Based Search**: Keyword and topic-based content discovery

### 🔧 **Advanced Features**
- **Respectful Rate Limiting**: Configurable delays between requests
- **Fallback Mechanisms**: Automatic fallback from API to HTTP scraping
- **Content Quality Control**: Score-based filtering and duplicate prevention
- **Metadata Preservation**: Complete Reddit metadata retention
- **Structured Data Output**: Clean, structured JSON responses

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │    │  HTTP Scraper   │    │   Browser       │
│   (Primary)     │    │   (Fallback)    │    │  (Last Resort)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Reddit Crawler  │
                    │    Service      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Reddit          │
                    │ Integration     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   GraphRAG      │
                    │   Knowledge     │
                    │     Graph       │
                    └─────────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
# Optional: Set Reddit API credentials for higher rate limits
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
export REDDIT_USER_AGENT="GraphRAG-RedditCrawler/1.0"
```

### 2. Start the Service

```bash
# Build and start the Reddit crawler service
docker compose up -d --build reddit-crawler

# Check service health
curl http://localhost:8003/health
```

### 3. Basic Crawl Example

```bash
# Crawl AI/ML content from specific subreddits
curl -X POST "http://localhost:8003/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "subreddits": ["MachineLearning", "artificial"],
    "max_posts": 10,
    "max_comments_per_post": 5,
    "comment_depth": 2,
    "auto_ingest": true
  }'
```

## API Reference

### Endpoints

#### `POST /crawl`
Start a new Reddit crawl with specified parameters.

**Request Body:**
```json
{
  "query": "search terms",
  "subreddits": ["subreddit1", "subreddit2"],
  "sort_by": "relevance",
  "time_filter": "month",
  "max_posts": 50,
  "max_comments_per_post": 20,
  "comment_depth": 2,
  "include_replies": true,
  "auto_ingest": true,
  "filter_nsfw": true
}
```

**Parameters:**
- `query` (string): Search query or topic
- `subreddits` (array, optional): Specific subreddits to search
- `sort_by` (string): Sort method - "relevance", "hot", "top", "new", "comments"
- `time_filter` (string): Time filter - "hour", "day", "week", "month", "year", "all"
- `max_posts` (integer): Maximum number of posts to crawl (default: 50)
- `max_comments_per_post` (integer): Maximum comments per post (default: 20)
- `comment_depth` (integer): Depth of comment recursion 1-3 (default: 2)
- `include_replies` (boolean): Include comment replies (default: true)
- `auto_ingest` (boolean): Automatically ingest into GraphRAG (default: true)
- `filter_nsfw` (boolean): Filter out NSFW content (default: true)

**Response:**
```json
{
  "crawl_id": "crawl_20250706_183458_5992",
  "status": "started",
  "posts_found": 0,
  "comments_found": 0,
  "total_content_length": 0,
  "estimated_processing_time": "2 minutes",
  "ingestion_status": "pending"
}
```

#### `GET /crawl/{crawl_id}/status`
Get the current status of a crawl.

**Response:**
```json
{
  "crawl_id": "crawl_20250706_183458_5992",
  "status": "completed",
  "progress": 100.0,
  "posts_processed": 3,
  "comments_processed": 8,
  "current_post": null,
  "error": null
}
```

#### `GET /crawl/{crawl_id}/results`
Get the results of a completed crawl.

**Response:**
```json
{
  "crawl_id": "crawl_20250706_183458_5992",
  "status": "completed",
  "results": [
    {
      "id": "1lnq3zt",
      "title": "Post Title",
      "content": "Post content...",
      "author": "username",
      "subreddit": "MachineLearning",
      "score": 308,
      "upvote_ratio": 0.89,
      "num_comments": 150,
      "comments": [...]
    }
  ],
  "statistics": {},
  "ingestion_status": "completed"
}
```

#### `GET /crawls`
List all crawls (active and completed).

#### `DELETE /crawl/{crawl_id}`
Cancel an active crawl.

#### `GET /health`
Service health check.

## Usage Examples

### 1. Technology News Monitoring

```bash
# Monitor technology discussions
curl -X POST "http://localhost:8003/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence OR machine learning OR deep learning",
    "subreddits": ["MachineLearning", "artificial", "deeplearning", "technology"],
    "sort_by": "hot",
    "time_filter": "day",
    "max_posts": 20,
    "max_comments_per_post": 10,
    "comment_depth": 2,
    "auto_ingest": true
  }'
```

### 2. Research Paper Discovery

```bash
# Find recent research papers
curl -X POST "http://localhost:8003/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "[R] OR [P] OR paper OR research",
    "subreddits": ["MachineLearning"],
    "sort_by": "new",
    "time_filter": "week",
    "max_posts": 15,
    "max_comments_per_post": 5,
    "comment_depth": 1,
    "auto_ingest": true
  }'
```

### 3. Community Discussion Analysis

```bash
# Analyze community discussions
curl -X POST "http://localhost:8003/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "discussion OR opinion OR thoughts",
    "subreddits": ["AskReddit", "technology", "futurology"],
    "sort_by": "top",
    "time_filter": "month",
    "max_posts": 30,
    "max_comments_per_post": 15,
    "comment_depth": 3,
    "auto_ingest": true
  }'
```

### 4. Trend Analysis

```bash
# Search across all subreddits for trending topics
curl -X POST "http://localhost:8003/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ChatGPT OR GPT-4 OR Claude OR LLM",
    "sort_by": "relevance",
    "time_filter": "month",
    "max_posts": 25,
    "max_comments_per_post": 8,
    "comment_depth": 2,
    "auto_ingest": true
  }'
```

## Configuration

### Environment Variables

- `REDDIT_CLIENT_ID`: Reddit API client ID (optional)
- `REDDIT_CLIENT_SECRET`: Reddit API client secret (optional)
- `REDDIT_USER_AGENT`: User agent for Reddit requests (optional)
- `GRAPHRAG_API_URL`: GraphRAG API endpoint (default: http://localhost:8000)

### Rate Limiting

The crawler implements respectful rate limiting:
- Default delay: 1 second between requests
- Configurable via `delay_between_requests` parameter
- Automatic backoff on rate limit errors

### Content Filtering

**Quality Filters:**
- Minimum score threshold (-10)
- Empty content filtering
- NSFW content filtering (configurable)
- Duplicate post prevention

**Comment Depth Control:**
- Depth 1: Only top-level comments
- Depth 2: Comments + first-level replies (recommended)
- Depth 3: Full comment tree (may be slow)

## Integration with GraphRAG

### Automatic Ingestion

When `auto_ingest: true`, crawled content is automatically:

1. **Formatted**: Reddit posts and comments are structured with metadata
2. **Processed**: Content goes through entity and relationship extraction
3. **Ingested**: Added to the knowledge graph with domain tagging
4. **Indexed**: Made searchable in the vector store

### Content Structure

Reddit content is ingested with the following structure:

```
Title: [Post Title]
Content: [Post Content]
Metadata: Author: username | Subreddit: r/subreddit | Score: 123 | Comments: 45

Comment: [Comment Body]
Parent Post: [Post Title]
Subreddit: r/subreddit
Metadata: Comment Author: username | Comment Score: 12 | Depth: 1
```

### Domain Tagging

All Reddit content is tagged with:
- `source`: "reddit"
- `domain`: subreddit name
- `content_type`: "reddit_post"
- `timestamp`: ingestion timestamp

## Monitoring and Troubleshooting

### Health Checks

```bash
# Service health
curl http://localhost:8003/health

# GraphRAG integration health
curl http://localhost:8000/health
```

### Log Monitoring

```bash
# View crawler logs
docker logs graphrag-reddit-crawler-1

# Follow logs in real-time
docker logs -f graphrag-reddit-crawler-1
```

### Common Issues

**1. No Posts Found**
- Check if subreddit exists and is accessible
- Verify query terms are not too specific
- Try different time filters or sort methods

**2. Slow Ingestion**
- Large posts take time to process through NER/relationship extraction
- Monitor GraphRAG API logs for processing status

**3. Rate Limiting**
- HTTP scraper has built-in rate limiting
- Consider setting up Reddit API credentials for higher limits

**4. Browser Issues**
- Browser automation is fallback only
- HTTP scraper is primary method and more reliable

## Performance Considerations

### Crawl Size Recommendations

- **Small Crawls**: 5-10 posts, 2-5 comments each
- **Medium Crawls**: 10-25 posts, 5-10 comments each  
- **Large Crawls**: 25-50 posts, 10-20 comments each

### Processing Time Estimates

- **Per Post**: ~30 seconds (including NER/relationship extraction)
- **Per Comment**: ~5 seconds
- **Network Latency**: 1-2 seconds per request

### Resource Usage

- **Memory**: ~500MB for crawler service
- **CPU**: Moderate during crawling, high during ingestion
- **Network**: Respectful rate limiting (1 req/sec default)

## Security and Privacy

### Data Handling

- Only public Reddit content is accessed
- No personal information is stored beyond what's publicly available
- NSFW content filtering available
- Respectful crawling practices

### API Security

- Optional Reddit API authentication
- Rate limiting and backoff mechanisms
- User agent identification
- No sensitive data in logs

## Future Enhancements

### Planned Features

- **Advanced Filtering**: Sentiment-based filtering, language detection
- **Real-time Streaming**: Live Reddit feed monitoring
- **Batch Processing**: Bulk historical data processing
- **Analytics Dashboard**: Crawl statistics and trends visualization
- **Custom Extractors**: Domain-specific entity extraction
- **Export Formats**: Multiple output formats (CSV, JSON, etc.)

### Integration Opportunities

- **Webhook Support**: Real-time notifications
- **Scheduled Crawls**: Automated periodic crawling
- **Multi-platform**: Twitter, HackerNews integration
- **Advanced Analytics**: Sentiment analysis, trend detection

## Contributing

To contribute to the Reddit crawler:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the GraphRAG system. See the main project license for details.

---

**Note**: This crawler respects Reddit's robots.txt and terms of service. Use responsibly and ensure compliance with Reddit's API terms when using API credentials. 