# Chunking Evaluation System

This document describes how to use the WikiSection benchmark to evaluate your semantic chunking performance.

## Overview

The evaluation system uses the WikiSection dataset to test how well your `SemanticChunker` identifies topic boundaries in Wikipedia articles. It compares your chunking results against human-annotated section boundaries.

## Features

- **Automatic dataset download**: Downloads WikiSection dataset automatically
- **Multiple evaluation modes**: Single subset or comparative evaluation
- **Baseline comparison**: Compare against fixed-size chunking
- **Multiple domains**: Disease and city articles in English and German
- **API and CLI interfaces**: Use via REST API or command line
- **Detailed metrics**: Precision, recall, F1-score, and boundary accuracy

## Quick Start

### 1. Using the API

Start your Docker container and use the evaluation endpoints:

```bash
# Check evaluation system status
curl -X GET "http://localhost:8000/evaluate/chunking/status"

# Run basic evaluation
curl -X POST "http://localhost:8000/evaluate/chunking" \
  -H "Content-Type: application/json" \
  -d '{
    "subset": "en_disease",
    "sample_size": 50,
    "force_download": false
  }'

# Run comparative evaluation
curl -X POST "http://localhost:8000/evaluate/chunking/comparative" \
  -H "Content-Type: application/json" \
  -d '{
    "subsets": ["en_disease", "en_city"],
    "sample_size": 50,
    "include_baseline": true,
    "baseline_chunk_size": 500
  }'
```

### 2. Using the CLI

Run evaluations from the command line:

```bash
# Enter the container
docker-compose exec api bash

# Basic evaluation
python run_chunking_evaluation.py --subset en_disease --sample-size 50

# Comparative evaluation with baseline
python run_chunking_evaluation.py --comparative --include-baseline --sample-size 50

# Save results to file
python run_chunking_evaluation.py --subset en_disease --output results.json

# Run with verbose logging
python run_chunking_evaluation.py --subset en_disease --verbose
```

### 3. Testing the System

Verify everything works with a quick test:

```bash
docker-compose exec api python test_chunking_evaluation.py
```

## API Endpoints

### GET `/evaluate/chunking/status`

Check if the evaluation system is ready and see available datasets.

**Response:**
```json
{
  "evaluation_system": "WikiSection",
  "dataset_available": true,
  "available_subsets": ["en_disease", "en_city", "de_disease", "de_city"],
  "semantic_chunker": "all-MiniLM-L6-v2",
  "supported_metrics": ["precision", "recall", "f1_score", "boundary_accuracy"]
}
```

### POST `/evaluate/chunking`

Run evaluation on a single WikiSection subset.

**Parameters:**
- `dataset`: Dataset to use (currently only "wikisection")
- `subset`: Subset to evaluate ("en_disease", "en_city", "de_disease", "de_city")
- `sample_size`: Number of documents to evaluate (default: 50)
- `force_download`: Force re-download dataset (default: false)

**Response:**
```json
{
  "evaluation_type": "WikiSection",
  "subset": "en_disease",
  "chunking_strategy": "semantic",
  "metrics": {
    "precision": 0.7234,
    "recall": 0.6891,
    "f1_score": 0.7058,
    "boundary_accuracy": "156/227",
    "boundary_accuracy_percent": 68.72
  }
}
```

### POST `/evaluate/chunking/comparative`

Run comparative evaluation across multiple subsets.

**Parameters:**
- `subsets`: List of subsets to evaluate
- `sample_size`: Number of documents per subset
- `include_baseline`: Include fixed-size chunking comparison
- `baseline_chunk_size`: Chunk size for baseline (default: 500)

## Understanding the Metrics

### Precision
Percentage of predicted boundaries that match ground truth boundaries (within tolerance).
- **High precision**: Few false positives, conservative chunking
- **Low precision**: Many false boundaries detected

### Recall
Percentage of ground truth boundaries that were correctly detected.
- **High recall**: Most actual boundaries found
- **Low recall**: Many boundaries missed

### F1-Score
Harmonic mean of precision and recall.
- **Best overall metric** for boundary detection quality
- Balances precision and recall

### Boundary Accuracy
Direct count of correctly identified boundaries.
- Shows absolute performance numbers
- Useful for understanding scale of the task

## Expected Performance

Based on research, you should expect:

- **Semantic chunking**: F1-score of 0.60-0.80
- **Fixed-size baseline**: F1-score of 0.30-0.50
- **Improvement**: 15-25% better than fixed-size

Your semantic chunker should significantly outperform fixed-size chunking because:
- It uses embedding similarity to detect topic shifts
- It preserves semantic coherence within chunks
- It adapts chunk sizes to content structure

## Datasets

### WikiSection Subsets

| Subset | Language | Domain | Documents | Focus |
|--------|----------|--------|-----------|--------|
| en_disease | English | Medical | 3,590 | Disease articles |
| en_city | English | Geographic | 19,539 | City articles |
| de_disease | German | Medical | 2,323 | Disease articles |
| de_city | German | Geographic | 12,537 | City articles |

### Ground Truth
Each document has human-annotated section boundaries marking where topics change. The evaluation measures how well your chunker identifies these natural breakpoints.

## Troubleshooting

### Dataset Download Issues
```bash
# Force re-download
curl -X POST "http://localhost:8000/evaluate/chunking" \
  -H "Content-Type: application/json" \
  -d '{"force_download": true}'
```

### Memory Issues
Reduce sample size for large evaluations:
```bash
python run_chunking_evaluation.py --sample-size 20
```

### Debugging Performance
Enable verbose logging:
```bash
python run_chunking_evaluation.py --verbose
```

## Files Created

- `./evaluation_data/`: Downloaded datasets
- `./evaluation_data/wikisection/`: Extracted WikiSection files
- `results.json`: Evaluation results (if --output used)

## Integration with Your Workflow

### Continuous Evaluation
Add to your CI/CD pipeline:
```bash
# Quick sanity check
python run_chunking_evaluation.py --subset en_disease --sample-size 10

# Full evaluation for releases
python run_chunking_evaluation.py --comparative --include-baseline --output release_eval.json
```

### Performance Monitoring
Track metrics over time:
- F1-score should improve as you tune your chunker
- Compare different chunking strategies
- Monitor performance across domains (medical vs. geographic)

### Development Iteration
1. Modify your `SemanticChunker` parameters
2. Run evaluation: `python run_chunking_evaluation.py --subset en_disease --sample-size 20`
3. Check if F1-score improved
4. Iterate until satisfied

## Advanced Usage

### Custom Evaluation
Modify `wikisection_evaluator.py` to:
- Change tolerance for boundary matching
- Add custom metrics
- Test different chunking strategies
- Evaluate on custom datasets

### Research Applications
Use for academic research:
- Compare different embedding models
- Test novel chunking algorithms
- Analyze performance across domains/languages
- Generate publication-ready results

## References

- [WikiSection Dataset](https://github.com/sebastianarnold/WikiSection)
- [SECTOR Paper](https://arxiv.org/abs/1908.02151) - Original WikiSection research
- [Chunking Evaluation Research](https://research.trychroma.com/evaluating-chunking) - Modern chunking evaluation methods 