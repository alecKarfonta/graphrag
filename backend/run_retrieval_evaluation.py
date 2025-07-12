#!/usr/bin/env python3
"""
Command-line script to run retrieval evaluations using GutenQA dataset.
"""

import argparse
import logging
import sys
import json
from gutenqa_evaluator import GutenQAEvaluator, format_retrieval_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Evaluate retrieval performance using GutenQA dataset')
    
    parser.add_argument(
        '--book-name', 
        type=str, 
        default='A_Christmas_Carol_-_Charles_Dickens',
        help='Book name to evaluate (default: A_Christmas_Carol_-_Charles_Dickens)'
    )
    
    parser.add_argument(
        '--max-questions', 
        type=int, 
        default=30,
        help='Maximum number of questions to evaluate (default: 30)'
    )
    
    parser.add_argument(
        '--method', 
        type=str, 
        choices=['baseline', 'hybrid', 'both'],
        default='both',
        help='Evaluation method: baseline (Contriever), hybrid (your system), or both'
    )
    
    parser.add_argument(
        '--data-dir', 
        type=str, 
        default='./retrieval_evaluation_data',
        help='Directory to store evaluation data'
    )
    
    parser.add_argument(
        '--force-download', 
        action='store_true',
        help='Force re-download of GutenQA dataset'
    )
    
    parser.add_argument(
        '--multiple-books', 
        nargs='+',
        help='Evaluate multiple books (space-separated)'
    )
    
    parser.add_argument(
        '--list-books', 
        action='store_true',
        help='List available books and exit'
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
        logger.info("Initializing GutenQA evaluator...")
        evaluator = GutenQAEvaluator(data_dir=args.data_dir)
        
        # Load dataset
        logger.info("Loading GutenQA dataset...")
        if not evaluator.load_gutenqa_dataset(force_download=args.force_download):
            logger.error("Failed to load GutenQA dataset")
            sys.exit(1)
        
        # List books if requested
        if args.list_books:
            available_books = evaluator.get_available_books()
            print("\n📚 Available Books in GutenQA Dataset:")
            print("=" * 50)
            for i, book in enumerate(available_books, 1):
                print(f"{i:3d}. {book}")
            print(f"\nTotal: {len(available_books)} books")
            sys.exit(0)
        
        # Multiple books evaluation
        if args.multiple_books:
            logger.info(f"Running evaluation on multiple books: {args.multiple_books}")
            
            # Check if books exist
            available_books = evaluator.get_available_books()
            missing_books = [book for book in args.multiple_books if book not in available_books]
            if missing_books:
                logger.error(f"Books not found: {missing_books}")
                logger.info(f"Available books: {available_books[:10]}...")
                sys.exit(1)
            
            # Run evaluation
            results = evaluator.evaluate_multiple_books(args.multiple_books, args.max_questions)
            
            # Generate report
            report = format_retrieval_report(results)
            print("\n" + report)
            
            # Save results if output file specified
            if args.output:
                output_data = {
                    "evaluation_type": "GutenQA Multiple Books",
                    "books_evaluated": args.multiple_books,
                    "max_questions_per_book": args.max_questions,
                    "method": args.method,
                    "results": {}
                }
                
                for book_name, book_results in results.items():
                    output_data["results"][book_name] = {}
                    for method, result in book_results.items():
                        output_data["results"][book_name][method] = {
                            "dcg_at_1": result.dcg_at_1,
                            "dcg_at_2": result.dcg_at_2,
                            "dcg_at_5": result.dcg_at_5,
                            "dcg_at_10": result.dcg_at_10,
                            "dcg_at_20": result.dcg_at_20,
                            "total_questions": result.total_questions,
                            "correct_retrievals": result.correct_retrievals,
                            "accuracy": result.correct_retrievals / result.total_questions,
                            "retrieval_method": result.retrieval_method
                        }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                logger.info(f"Results saved to {args.output}")
        
        else:
            # Single book evaluation
            logger.info(f"Running evaluation on book: {args.book_name}")
            
            # Check if book exists
            available_books = evaluator.get_available_books()
            if args.book_name not in available_books:
                logger.error(f"Book not found: {args.book_name}")
                logger.info(f"Available books: {available_books[:10]}...")
                sys.exit(1)
            
            results = {}
            
            # Run baseline evaluation
            if args.method in ['baseline', 'both']:
                try:
                    logger.info("Running baseline evaluation (Contriever)...")
                    baseline_result = evaluator.evaluate_baseline_retrieval(args.book_name, args.max_questions)
                    results['baseline'] = baseline_result
                except Exception as e:
                    logger.error(f"Baseline evaluation failed: {e}")
            
            # Run hybrid evaluation
            if args.method in ['hybrid', 'both']:
                try:
                    logger.info("Running hybrid evaluation (your system)...")
                    hybrid_result = evaluator.evaluate_hybrid_retrieval(args.book_name, args.max_questions)
                    results['hybrid'] = hybrid_result
                except Exception as e:
                    logger.error(f"Hybrid evaluation failed: {e}")
            
            if not results:
                logger.error("No evaluation results obtained")
                sys.exit(1)
            
            # Print results
            print("\n" + "="*60)
            print("GUTENQA RETRIEVAL EVALUATION RESULT")
            print("="*60)
            print(f"Book: {args.book_name}")
            print(f"Questions Evaluated: {args.max_questions}")
            print(f"Method: {args.method}")
            
            for method, result in results.items():
                print(f"\n--- {result.retrieval_method.upper()} ---")
                print(f"Total Questions: {result.total_questions}")
                print(f"Correct@1: {result.correct_retrievals}/{result.total_questions} ({result.correct_retrievals/result.total_questions*100:.1f}%)")
                print(f"DCG@1: {result.dcg_at_1:.4f}")
                print(f"DCG@2: {result.dcg_at_2:.4f}")
                print(f"DCG@5: {result.dcg_at_5:.4f}")
                print(f"DCG@10: {result.dcg_at_10:.4f}")
                print(f"DCG@20: {result.dcg_at_20:.4f}")
            
            # Comparison if both methods run
            if len(results) == 2:
                baseline_dcg1 = results['baseline'].dcg_at_1
                hybrid_dcg1 = results['hybrid'].dcg_at_1
                improvement = (hybrid_dcg1 - baseline_dcg1) / baseline_dcg1 * 100 if baseline_dcg1 > 0 else 0
                
                print("\n" + "-"*40)
                print("COMPARISON")
                print("-"*40)
                print(f"Baseline DCG@1: {baseline_dcg1:.4f}")
                print(f"Hybrid DCG@1: {hybrid_dcg1:.4f}")
                print(f"Improvement: {improvement:+.1f}%")
            
            # Save results if output file specified
            if args.output:
                output_data = {
                    "evaluation_type": "GutenQA",
                    "book_name": args.book_name,
                    "max_questions": args.max_questions,
                    "method": args.method,
                    "results": {}
                }
                
                for method, result in results.items():
                    output_data["results"][method] = {
                        "dcg_at_1": result.dcg_at_1,
                        "dcg_at_2": result.dcg_at_2,
                        "dcg_at_5": result.dcg_at_5,
                        "dcg_at_10": result.dcg_at_10,
                        "dcg_at_20": result.dcg_at_20,
                        "total_questions": result.total_questions,
                        "correct_retrievals": result.correct_retrievals,
                        "accuracy": result.correct_retrievals / result.total_questions,
                        "retrieval_method": result.retrieval_method
                    }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                logger.info(f"Results saved to {args.output}")
        
        logger.info("Evaluation completed successfully!")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 