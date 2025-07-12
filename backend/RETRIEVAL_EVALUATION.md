# Retrieval Evaluation System

This document describes how to use the GutenQA dataset to evaluate your retrieval system performance against benchmark datasets.

## Overview

The retrieval evaluation system uses the [GutenQA dataset](https://huggingface.co/datasets/LumberChunker/GutenQA) to test how well your `HybridRetriever` finds relevant information for given questions. It compares your system against a baseline Contriever model using established metrics.

## Features

- **Automatic dataset download**: Downloads GutenQA dataset from HuggingFace automatically
- **Baseline comparison**: Compare against Facebook's Contriever model
- **Multiple evaluation modes**: Single book, multiple books, or comparative evaluation
- **Comprehensive metrics**: DCG@1, DCG@2, DCG@5, DCG@10, DCG@20, and accuracy
- **100 classic books**: Evaluate on diverse literature from Project Gutenberg
- **API and CLI interfaces**: Use via REST API or command line
- **3,000+ questions**: Large-scale evaluation with generated QA pairs

## Quick Start

### 1. Using the API

Start your Docker container and use the retrieval evaluation endpoints:

```bash
# Check evaluation system status
curl -X GET "http://localhost:8000/evaluate/retrieval/status"

# Run basic evaluation
curl -X POST "http://localhost:8000/evaluate/retrieval" \
  -H "Content-Type: application/json" \
  -d '{
    "book_name": "A_Christmas_Carol_-_Charles_Dickens",
    "max_questions": 30,
    "method": "both",
    "force_download": false
  }'

# Run comparative evaluation
curl -X POST "http://localhost:8000/evaluate/retrieval/comparative" \
  -H "Content-Type: application/json" \
  -d '{
    "book_names": ["A_Christmas_Carol_-_Charles_Dickens", "Pride_and_Prejudice_-_Jane_Austen"],
    "max_questions_per_book": 20,
    "include_baseline": true
  }'
```

### 2. Using the CLI

Run evaluations from the command line:

```bash
# Enter the container
docker-compose exec api bash

# List available books
python run_retrieval_evaluation.py --list-books

# Basic evaluation
python run_retrieval_evaluation.py --book-name "A_Christmas_Carol_-_Charles_Dickens" --max-questions 30

# Compare multiple books
python run_retrieval_evaluation.py --multiple-books "A_Christmas_Carol_-_Charles_Dickens" "Pride_and_Prejudice_-_Jane_Austen" --max-questions 20

# Save results to file
python run_retrieval_evaluation.py --book-name "A_Christmas_Carol_-_Charles_Dickens" --output results.json

# Run with verbose logging
python run_retrieval_evaluation.py --book-name "A_Christmas_Carol_-_Charles_Dickens" --verbose
```

### 3. Testing the System

Verify everything works with a quick test:

```bash
docker-compose exec api python test_retrieval_evaluation.py
```

## API Endpoints

### GET `/evaluate/retrieval/status`

Check if the retrieval evaluation system is ready and see available books.

**Response:**
```json
{
  "evaluation_system": "GutenQA",
  "dataset_available": true,
  "baseline_model": "facebook/contriever",
  "hybrid_retriever": "HybridRetriever (vector + graph + keyword)",
  "supported_metrics": ["DCG@1", "DCG@2", "DCG@5", "DCG@10", "DCG@20", "accuracy"],
  "available_books_sample": ["A_Christmas_Carol_-_Charles_Dickens", "Pride_and_Prejudice_-_Jane_Austen"],
  "total_books": 100
}
```

### POST `/evaluate/retrieval`

Run retrieval evaluation on a single book.

**Parameters:**
- `book_name`: Book to evaluate (default: "A_Christmas_Carol_-_Charles_Dickens")
- `max_questions`: Number of questions to evaluate (default: 30)
- `method`: Evaluation method ("baseline", "hybrid", "both")
- `force_download`: Force re-download dataset (default: false)

**Response:**
```json
{
  "evaluation_type": "GutenQA",
  "book_name": "A_Christmas_Carol_-_Charles_Dickens",
  "max_questions": 30,
  "results": {
    "baseline": {
      "dcg_at_1": 0.3245,
      "dcg_at_10": 0.4872,
      "accuracy": 0.4333,
      "total_questions": 30,
      "correct_retrievals": 13
    },
    "hybrid": {
      "dcg_at_1": 0.4156,
      "dcg_at_10": 0.6234,
      "accuracy": 0.5667,
      "total_questions": 30,
      "correct_retrievals": 17
    }
  }
}
```

### POST `/evaluate/retrieval/comparative`

Run comparative retrieval evaluation across multiple books.

**Parameters:**
- `book_names`: List of books to evaluate
- `max_questions_per_book`: Questions per book
- `include_baseline`: Include baseline comparison

## Understanding the Metrics

### DCG@k (Discounted Cumulative Gain)
Measures the quality of ranking in retrieval results.
- **DCG@1**: How often the first result is correct
- **DCG@10**: Quality considering top 10 results with position discount
- **Higher is better**: Perfect score depends on relevance patterns

### Accuracy (Correct@1)
Percentage of questions where the correct chunk appears in the top-1 result.
- **Direct interpretability**: 60% accuracy means 6 out of 10 questions answered correctly
- **Critical metric**: Most users only look at the first result

### Expected Performance

Based on research and the GutenQA paper, you should expect:

- **Contriever baseline**: DCG@1 of 0.25-0.35 (25-35% accuracy)
- **Your hybrid system**: DCG@1 of 0.35-0.50 (35-50% accuracy) 
- **Improvement**: 15-30% better than baseline

Your hybrid retriever should outperform the baseline because:
- It combines vector, graph, and keyword search
- It uses domain-specific entity relationships
- It has semantic chunking aligned with content structure

## Available Books

The GutenQA dataset includes 100 classic books from Project Gutenberg:

### Popular Examples
- `A_Christmas_Carol_-_Charles_Dickens`
- `Pride_and_Prejudice_-_Jane_Austen`
- `The_Adventures_of_Tom_Sawyer_-_Mark_Twain`
- `Alice_s_Adventures_in_Wonderland_-_Lewis_Carroll`
- `Frankenstein_-_Mary_Wollstonecraft_Shelley`
- `The_Picture_of_Dorian_Gray_-_Oscar_Wilde`
- `The_Time_Machine_-_H_G_Wells`
- `Dracula_-_Bram_Stoker`

### Question Types
Each book has ~30 questions covering:
- **Plot details**: "What did Scrooge see in his bedroom?"
- **Character information**: "Who is Elizabeth Bennet's father?"
- **Setting details**: "Where does the story take place?"
- **Thematic elements**: "What is the main theme of the story?"

## Troubleshooting

### Dataset Download Issues
```bash
# Force re-download
curl -X POST "http://localhost:8000/evaluate/retrieval" \
  -H "Content-Type: application/json" \
  -d '{"force_download": true}'
```

### Memory Issues
Reduce question count for large evaluations:
```bash
python run_retrieval_evaluation.py --max-questions 10
```

### Model Loading Issues
The baseline Contriever model requires ~1GB RAM and internet access for first-time download. If it fails:
```bash
# Run only hybrid evaluation
python run_retrieval_evaluation.py --method hybrid
```

### Debugging Performance
Enable verbose logging:
```bash
python run_retrieval_evaluation.py --verbose
```

## Files Created

- `./retrieval_evaluation_data/`: Downloaded datasets
- `./retrieval_evaluation_data/gutenqa_chunks.parquet`: Book chunks
- `./retrieval_evaluation_data/gutenqa_questions.parquet`: Questions and answers
- `results.json`: Evaluation results (if --output used)

## Integration with Your Workflow

### Continuous Evaluation
Add to your CI/CD pipeline:
```bash
# Quick sanity check
python run_retrieval_evaluation.py --book-name "A_Christmas_Carol_-_Charles_Dickens" --max-questions 10

# Full evaluation for releases
python run_retrieval_evaluation.py --multiple-books "A_Christmas_Carol_-_Charles_Dickens" "Pride_and_Prejudice_-_Jane_Austen" --output release_eval.json
```

### Performance Monitoring
Track metrics over time:
- DCG@1 should improve as you tune your retriever
- Compare different retrieval strategies
- Monitor performance across different book genres

### Development Iteration
1. Modify your `HybridRetriever` parameters
2. Run evaluation: `python run_retrieval_evaluation.py --book-name "A_Christmas_Carol_-_Charles_Dickens" --max-questions 20`
3. Check if DCG@1 improved
4. Iterate until satisfied

## Advanced Usage

### Custom Evaluation
Modify `gutenqa_evaluator.py` to:
- Test different embedding models
- Adjust DCG calculation parameters
- Add custom retrieval metrics
- Evaluate on custom question sets

### Research Applications
Use for academic research:
- Compare different retrieval architectures
- Test novel fusion strategies
- Analyze performance across literary genres
- Generate publication-ready results

### Book-Specific Analysis
Some books may be harder than others:
- **Dialogue-heavy**: May favor keyword search
- **Descriptive**: May favor semantic search
- **Plot-driven**: May favor graph relationships

## Performance Optimization

### Speed Improvements
- Use smaller question samples for development
- Cache embeddings between runs
- Run baseline evaluation separately if needed

### Accuracy Improvements
- Tune hybrid retriever weights
- Experiment with different chunk sizes
- Add book-specific preprocessing

## References

- [GutenQA Dataset](https://huggingface.co/datasets/LumberChunker/GutenQA)
- [LumberChunker Paper](https://arxiv.org/abs/2406.17526) - Original GutenQA research
- [Contriever Paper](https://arxiv.org/abs/2112.09118) - Baseline retriever model
- [Project Gutenberg](https://www.gutenberg.org/) - Source of the books 