#!/usr/bin/env python3
"""
Command-line script to run chunking evaluations using WikiSection dataset.
"""

import argparse
import logging
import sys
import json
from wikisection_evaluator import WikiSectionEvaluator, format_evaluation_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Evaluate chunking performance using WikiSection dataset')
    
    parser.add_argument(
        '--subset', 
        type=str, 
        default='en_disease',
        choices=['en_disease', 'en_city', 'de_disease', 'de_city'],
        help='WikiSection subset to evaluate on'
    )
    
    parser.add_argument(
        '--sample-size', 
        type=int, 
        default=50,
        help='Number of documents to evaluate (default: 50)'
    )
    
    parser.add_argument(
        '--data-dir', 
        type=str, 
        default='./evaluation_data',
        help='Directory to store evaluation data'
    )
    
    parser.add_argument(
        '--force-download', 
        action='store_true',
        help='Force re-download of WikiSection dataset'
    )
    
    parser.add_argument(
        '--comparative', 
        action='store_true',
        help='Run comparative evaluation across multiple subsets'
    )
    
    parser.add_argument(
        '--include-baseline', 
        action='store_true',
        help='Include fixed-size chunking baseline comparison'
    )
    
    parser.add_argument(
        '--baseline-chunk-size', 
        type=int, 
        default=500,
        help='Chunk size for baseline comparison (default: 500)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file to save results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize evaluator
        logger.info("Initializing WikiSection evaluator...")
        evaluator = WikiSectionEvaluator(data_dir=args.data_dir)
        
        # Download dataset if needed
        logger.info("Checking for WikiSection dataset...")
        if not evaluator.download_dataset(force_download=args.force_download):
            logger.error("Failed to download WikiSection dataset")
            sys.exit(1)
        
        if args.comparative:
            # Run comparative evaluation
            logger.info("Running comparative evaluation...")
            subsets = ['en_disease', 'en_city', 'de_disease', 'de_city']
            results = evaluator.run_comparative_evaluation(subsets, args.sample_size)
            
            # Add baseline if requested
            if args.include_baseline and results:
                logger.info("Adding baseline comparison...")
                first_subset = list(results.keys())[0]
                documents = evaluator.load_wikisection_data(first_subset)
                
                if documents:
                    baseline_comparison = evaluator.compare_with_baseline(
                        documents[:args.sample_size], args.baseline_chunk_size
                    )
                    results[f"{first_subset}_baseline"] = baseline_comparison["baseline"]
            
            # Generate report
            report = format_evaluation_report(results)
            print("\n" + report)
            
            # Summary
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            best_f1 = max(r.f1_score for r in results.values())
            best_precision = max(r.precision for r in results.values())
            best_recall = max(r.recall for r in results.values())
            
            print(f"Best F1-Score: {best_f1:.4f}")
            print(f"Best Precision: {best_precision:.4f}")
            print(f"Best Recall: {best_recall:.4f}")
            
            # Save results if output file specified
            if args.output:
                output_data = {
                    "evaluation_type": "WikiSection Comparative",
                    "subsets_evaluated": subsets,
                    "sample_size": args.sample_size,
                    "include_baseline": args.include_baseline,
                    "results": {
                        subset_name: {
                            "precision": result.precision,
                            "recall": result.recall,
                            "f1_score": result.f1_score,
                            "total_documents": result.total_documents,
                            "correct_boundaries": result.correct_boundaries,
                            "total_boundaries": result.total_boundaries,
                            "dataset_name": result.dataset_name,
                            "chunking_method": result.chunking_method
                        }
                        for subset_name, result in results.items()
                    },
                    "summary": {
                        "best_f1": best_f1,
                        "best_precision": best_precision,
                        "best_recall": best_recall
                    }
                }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                logger.info(f"Results saved to {args.output}")
        
        else:
            # Run single subset evaluation
            logger.info(f"Running evaluation on subset: {args.subset}")
            documents = evaluator.load_wikisection_data(args.subset)
            
            if not documents:
                logger.error(f"No documents found for subset: {args.subset}")
                sys.exit(1)
            
            # Run evaluation
            result = evaluator.evaluate_chunking(documents, sample_size=args.sample_size)
            
            # Print results
            print("\n" + "="*60)
            print("WIKISECTION CHUNKING EVALUATION RESULT")
            print("="*60)
            print(f"Dataset: {result.dataset_name}")
            print(f"Subset: {args.subset}")
            print(f"Method: {result.chunking_method}")
            print(f"Documents: {result.total_documents}")
            print(f"Sample Size: {min(args.sample_size, len(documents))}")
            print(f"Precision: {result.precision:.4f}")
            print(f"Recall: {result.recall:.4f}")
            print(f"F1-Score: {result.f1_score:.4f}")
            print(f"Boundary Accuracy: {result.correct_boundaries}/{result.total_boundaries} ({result.correct_boundaries/result.total_boundaries*100:.2f}%)")
            
            # Include baseline comparison if requested
            if args.include_baseline:
                logger.info("Running baseline comparison...")
                baseline_comparison = evaluator.compare_with_baseline(
                    documents[:args.sample_size], args.baseline_chunk_size
                )
                
                semantic_result = baseline_comparison["semantic"]
                baseline_result = baseline_comparison["baseline"]
                
                print("\n" + "-"*40)
                print("BASELINE COMPARISON")
                print("-"*40)
                print(f"Semantic Chunking F1: {semantic_result.f1_score:.4f}")
                print(f"Fixed-size Chunking F1: {baseline_result.f1_score:.4f}")
                print(f"Improvement: {semantic_result.f1_score - baseline_result.f1_score:.4f}")
                print(f"Relative Improvement: {((semantic_result.f1_score - baseline_result.f1_score) / baseline_result.f1_score * 100):.2f}%")
            
            # Save results if output file specified
            if args.output:
                output_data = {
                    "evaluation_type": "WikiSection",
                    "subset": args.subset,
                    "sample_size": min(args.sample_size, len(documents)),
                    "total_documents": len(documents),
                    "chunking_strategy": "semantic",
                    "model": "all-MiniLM-L6-v2",
                    "metrics": {
                        "precision": result.precision,
                        "recall": result.recall,
                        "f1_score": result.f1_score,
                        "boundary_accuracy": f"{result.correct_boundaries}/{result.total_boundaries}",
                        "boundary_accuracy_percent": round(result.correct_boundaries/result.total_boundaries*100, 2) if result.total_boundaries > 0 else 0.0
                    },
                    "results": {
                        "correct_boundaries": result.correct_boundaries,
                        "total_boundaries": result.total_boundaries,
                        "dataset_name": result.dataset_name,
                        "chunking_method": result.chunking_method
                    }
                }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                logger.info(f"Results saved to {args.output}")
        
        logger.info("Evaluation completed successfully!")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 