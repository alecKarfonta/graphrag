from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from entity_extractor import EntityExtractor, Entity, Relationship, ExtractionResult
from hybrid_retriever import HybridRetriever
from query_processor import QueryProcessor
from knowledge_graph_builder import KnowledgeGraphBuilder
from neo4j_conn import get_neo4j_session
import json
import time
from datetime import datetime
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    confidence_scores: List[float]
    processing_time: float
    additional_metrics: Dict[str, Any]

@dataclass
class TestCase:
    """Represents a test case for evaluation."""
    id: str
    input_data: Any
    expected_output: Any
    test_type: str
    domain: str = "general"
    metadata: Dict[str, Any] = None

@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    test_case: TestCase
    actual_output: Any
    metrics: EvaluationMetrics
    passed: bool
    error_message: Optional[str] = None

class GraphRAGEvaluator:
    """Comprehensive evaluation framework for Graph RAG system."""
    
    def __init__(self):
        """Initialize the evaluator with all necessary components."""
        try:
            self.entity_extractor = EntityExtractor()
            self.hybrid_retriever = HybridRetriever()
            self.query_processor = QueryProcessor()
            self.knowledge_graph_builder = KnowledgeGraphBuilder()
            logger.info("✅ GraphRAG Evaluator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GraphRAG Evaluator: {e}")
            raise
    
    def evaluate_entity_extraction(self, test_documents: List[str], ground_truth: Dict) -> Dict[str, EvaluationMetrics]:
        """Evaluate entity extraction accuracy against ground truth."""
        logger.info(f"Starting entity extraction evaluation with {len(test_documents)} documents")
        
        results = {
            'overall': EvaluationMetrics(0.0, 0.0, 0.0, 0.0, [], 0.0, {}),
            'by_entity_type': {},
            'by_document': []
        }
        
        total_start_time = time.time()
        all_extracted_entities = []
        all_ground_truth_entities = []
        
        for i, doc in enumerate(test_documents):
            doc_start_time = time.time()
            
            try:
                # Extract entities from document
                extraction_result = self.entity_extractor.extract_entities_and_relations(doc)
                extracted_entities = extraction_result.entities
                
                # Get ground truth for this document
                doc_ground_truth = ground_truth.get(f"doc_{i}", [])
                
                # Calculate metrics for this document
                doc_metrics = self._calculate_entity_metrics(extracted_entities, doc_ground_truth)
                doc_metrics.processing_time = time.time() - doc_start_time
                
                results['by_document'].append({
                    'document_id': f"doc_{i}",
                    'metrics': doc_metrics,
                    'extracted_count': len(extracted_entities),
                    'ground_truth_count': len(doc_ground_truth)
                })
                
                all_extracted_entities.extend(extracted_entities)
                all_ground_truth_entities.extend(doc_ground_truth)
                
            except Exception as e:
                logger.error(f"Error evaluating document {i}: {e}")
                continue
        
        # Calculate overall metrics
        overall_metrics = self._calculate_entity_metrics(all_extracted_entities, all_ground_truth_entities)
        overall_metrics.processing_time = time.time() - total_start_time
        results['overall'] = overall_metrics
        
        # Calculate metrics by entity type
        entity_types = set([e.entity_type for e in all_extracted_entities] + 
                         [e.get('type', 'UNKNOWN') for e in all_ground_truth_entities])
        
        for entity_type in entity_types:
            type_extracted = [e for e in all_extracted_entities if e.entity_type == entity_type]
            type_ground_truth = [e for e in all_ground_truth_entities if e.get('type') == entity_type]
            
            type_metrics = self._calculate_entity_metrics(type_extracted, type_ground_truth)
            results['by_entity_type'][entity_type] = type_metrics
        
        logger.info(f"Entity extraction evaluation completed. Overall F1: {overall_metrics.f1_score:.3f}")
        return results
    
    def evaluate_query_responses(self, test_queries: List[str], expected_answers: List[str]) -> Dict[str, EvaluationMetrics]:
        """Evaluate query response accuracy and relevance."""
        logger.info(f"Starting query response evaluation with {len(test_queries)} queries")
        
        results = {
            'overall': EvaluationMetrics(0.0, 0.0, 0.0, 0.0, [], 0.0, {}),
            'by_query_type': {},
            'response_times': []
        }
        
        total_start_time = time.time()
        all_actual_responses = []
        all_expected_responses = []
        
        for i, (query, expected) in enumerate(zip(test_queries, expected_answers)):
            query_start_time = time.time()
            
            try:
                # Process query through the system
                actual_response = self.query_processor.process_query(query)
                
                # Calculate response time
                response_time = time.time() - query_start_time
                results['response_times'].append(response_time)
                
                # Calculate similarity between actual and expected responses
                similarity_score = self._calculate_response_similarity(actual_response, expected)
                
                all_actual_responses.append(actual_response)
                all_expected_responses.append(expected)
                
                logger.info(f"Query {i+1}/{len(test_queries)}: Response time {response_time:.2f}s, Similarity: {similarity_score:.3f}")
                
            except Exception as e:
                logger.error(f"Error processing query {i}: {e}")
                continue
        
        # Calculate overall metrics
        overall_metrics = self._calculate_response_metrics(all_actual_responses, all_expected_responses)
        overall_metrics.processing_time = time.time() - total_start_time
        overall_metrics.additional_metrics = {
            'avg_response_time': np.mean(results['response_times']) if results['response_times'] else 0.0,
            'max_response_time': max(results['response_times']) if results['response_times'] else 0.0,
            'min_response_time': min(results['response_times']) if results['response_times'] else 0.0
        }
        results['overall'] = overall_metrics
        
        logger.info(f"Query response evaluation completed. Overall accuracy: {overall_metrics.accuracy:.3f}")
        return results
    
    def evaluate_graph_completeness(self) -> Dict[str, Any]:
        """Evaluate the completeness and quality of the knowledge graph."""
        logger.info("Starting knowledge graph completeness evaluation")
        
        try:
            with get_neo4j_session() as session:
                # Get graph statistics
                stats_query = """
                MATCH (n)
                WITH count(n) as total_nodes, count(DISTINCT labels(n)) as node_types
                MATCH ()-[r]->()
                RETURN 
                    total_nodes,
                    node_types,
                    count(r) as total_relationships,
                    count(DISTINCT type(r)) as relationship_types
                """
                stats_result = session.run(stats_query).single()
                
                # Get entity distribution
                entity_dist_query = """
                MATCH (e:Entity)
                RETURN e.type as entity_type, count(e) as count
                ORDER BY count DESC
                """
                entity_dist = session.run(entity_dist_query)
                entity_distribution = {record['entity_type']: record['count'] for record in entity_dist}
                
                # Get relationship distribution
                rel_dist_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
                """
                rel_dist = session.run(rel_dist_query)
                relationship_distribution = {record['relationship_type']: record['count'] for record in rel_dist}
                
                # Calculate graph density
                total_nodes = stats_result['total_nodes']
                total_relationships = stats_result['total_relationships']
                max_possible_relationships = total_nodes * (total_nodes - 1)
                graph_density = total_relationships / max_possible_relationships if max_possible_relationships > 0 else 0
                
                # Calculate connectivity
                connectivity_query = """
                MATCH (n)
                WITH count(n) as total_nodes
                MATCH (n)-[r]-()
                WITH total_nodes, count(DISTINCT n) as connected_nodes
                RETURN connected_nodes, total_nodes, 
                       toFloat(connected_nodes) / total_nodes as connectivity_ratio
                """
                connectivity_result = session.run(connectivity_query).single()
                
                completeness_metrics = {
                    'total_nodes': total_nodes,
                    'node_types': stats_result['node_types'],
                    'total_relationships': total_relationships,
                    'relationship_types': stats_result['relationship_types'],
                    'entity_distribution': entity_distribution,
                    'relationship_distribution': relationship_distribution,
                    'graph_density': graph_density,
                    'connectivity_ratio': connectivity_result['connectivity_ratio'],
                    'avg_relationships_per_node': total_relationships / total_nodes if total_nodes > 0 else 0
                }
                
                logger.info(f"Graph completeness evaluation completed. Nodes: {total_nodes}, Relationships: {total_relationships}")
                return completeness_metrics
                
        except Exception as e:
            logger.error(f"Error evaluating graph completeness: {e}")
            return {}
    
    def evaluate_retrieval_relevance(self, test_queries: List[str], relevance_scores: List[float]) -> Dict[str, EvaluationMetrics]:
        """Evaluate the relevance of retrieved results."""
        logger.info(f"Starting retrieval relevance evaluation with {len(test_queries)} queries")
        
        results = {
            'overall': EvaluationMetrics(0.0, 0.0, 0.0, 0.0, [], 0.0, {}),
            'by_query_type': {},
            'relevance_distribution': []
        }
        
        total_start_time = time.time()
        
        for i, (query, expected_relevance) in enumerate(zip(test_queries, relevance_scores)):
            try:
                # Perform retrieval
                search_results = self.hybrid_retriever.retrieve(query, top_k=10)
                
                # Calculate actual relevance scores
                actual_relevance_scores = [result.score for result in search_results]
                
                # Calculate relevance metrics
                avg_relevance = np.mean(actual_relevance_scores) if actual_relevance_scores else 0.0
                max_relevance = max(actual_relevance_scores) if actual_relevance_scores else 0.0
                
                # Compare with expected relevance
                relevance_accuracy = 1.0 - abs(avg_relevance - expected_relevance)
                
                results['relevance_distribution'].append({
                    'query': query,
                    'expected_relevance': expected_relevance,
                    'actual_avg_relevance': avg_relevance,
                    'actual_max_relevance': max_relevance,
                    'accuracy': relevance_accuracy
                })
                
            except Exception as e:
                logger.error(f"Error evaluating retrieval for query {i}: {e}")
                continue
        
        # Calculate overall metrics
        if results['relevance_distribution']:
            overall_accuracy = np.mean([r['accuracy'] for r in results['relevance_distribution']])
            avg_relevance = np.mean([r['actual_avg_relevance'] for r in results['relevance_distribution']])
            
            overall_metrics = EvaluationMetrics(
                precision=overall_accuracy,
                recall=overall_accuracy,
                f1_score=overall_accuracy,
                accuracy=overall_accuracy,
                confidence_scores=[r['accuracy'] for r in results['relevance_distribution']],
                processing_time=time.time() - total_start_time,
                additional_metrics={
                    'avg_relevance_score': avg_relevance,
                    'relevance_std': np.std([r['actual_avg_relevance'] for r in results['relevance_distribution']])
                }
            )
            results['overall'] = overall_metrics
        
        logger.info(f"Retrieval relevance evaluation completed. Overall accuracy: {overall_metrics.accuracy:.3f}")
        return results
    
    def _calculate_entity_metrics(self, extracted_entities: List[Entity], ground_truth_entities: List[Dict]) -> EvaluationMetrics:
        """Calculate precision, recall, and F1 score for entity extraction."""
        if not extracted_entities and not ground_truth_entities:
            return EvaluationMetrics(1.0, 1.0, 1.0, 1.0, [], 0.0, {})
        
        if not extracted_entities or not ground_truth_entities:
            return EvaluationMetrics(0.0, 0.0, 0.0, 0.0, [], 0.0, {})
        
        # Convert to comparable format
        extracted_names = [e.name.lower() for e in extracted_entities]
        ground_truth_names = [e.get('name', '').lower() for e in ground_truth_entities]
        
        # Calculate true positives, false positives, false negatives
        true_positives = len(set(extracted_names) & set(ground_truth_names))
        false_positives = len(extracted_names) - true_positives
        false_negatives = len(ground_truth_names) - true_positives
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = true_positives / len(ground_truth_names) if ground_truth_names else 0.0
        
        confidence_scores = [e.confidence for e in extracted_entities]
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy,
            confidence_scores=confidence_scores,
            processing_time=0.0,
            additional_metrics={
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives
            }
        )
    
    def _calculate_response_metrics(self, actual_responses: List[str], expected_responses: List[str]) -> EvaluationMetrics:
        """Calculate metrics for query responses."""
        if not actual_responses or not expected_responses:
            return EvaluationMetrics(0.0, 0.0, 0.0, 0.0, [], 0.0, {})
        
        # Calculate similarity scores
        similarity_scores = []
        for actual, expected in zip(actual_responses, expected_responses):
            similarity = self._calculate_response_similarity(actual, expected)
            similarity_scores.append(similarity)
        
        # Calculate overall metrics
        avg_similarity = np.mean(similarity_scores)
        accuracy = avg_similarity  # Use similarity as accuracy proxy
        
        return EvaluationMetrics(
            precision=accuracy,
            recall=accuracy,
            f1_score=accuracy,
            accuracy=accuracy,
            confidence_scores=similarity_scores,
            processing_time=0.0,
            additional_metrics={
                'avg_similarity': avg_similarity,
                'similarity_std': np.std(similarity_scores)
            }
        )
    
    def _calculate_response_similarity(self, actual: str, expected: str) -> float:
        """Calculate similarity between actual and expected responses."""
        if not actual or not expected:
            return 0.0
        
        # Simple word overlap similarity
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())
        
        if not actual_words or not expected_words:
            return 0.0
        
        intersection = len(actual_words & expected_words)
        union = len(actual_words | expected_words)
        
        return intersection / union if union > 0 else 0.0
    
    def generate_evaluation_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive evaluation report."""
        report = []
        report.append("=" * 80)
        report.append("GRAPH RAG SYSTEM EVALUATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Entity Extraction Results
        if 'entity_extraction' in results:
            report.append("ENTITY EXTRACTION EVALUATION")
            report.append("-" * 40)
            overall = results['entity_extraction']['overall']
            report.append(f"Overall F1 Score: {overall.f1_score:.3f}")
            report.append(f"Overall Precision: {overall.precision:.3f}")
            report.append(f"Overall Recall: {overall.recall:.3f}")
            report.append(f"Processing Time: {overall.processing_time:.2f}s")
            report.append("")
        
        # Query Response Results
        if 'query_responses' in results:
            report.append("QUERY RESPONSE EVALUATION")
            report.append("-" * 40)
            overall = results['query_responses']['overall']
            report.append(f"Overall Accuracy: {overall.accuracy:.3f}")
            if 'avg_response_time' in overall.additional_metrics:
                report.append(f"Average Response Time: {overall.additional_metrics['avg_response_time']:.2f}s")
            report.append("")
        
        # Graph Completeness Results
        if 'graph_completeness' in results:
            report.append("KNOWLEDGE GRAPH COMPLETENESS")
            report.append("-" * 40)
            graph_stats = results['graph_completeness']
            report.append(f"Total Nodes: {graph_stats.get('total_nodes', 0)}")
            report.append(f"Total Relationships: {graph_stats.get('total_relationships', 0)}")
            report.append(f"Graph Density: {graph_stats.get('graph_density', 0):.4f}")
            report.append(f"Connectivity Ratio: {graph_stats.get('connectivity_ratio', 0):.3f}")
            report.append("")
        
        # Retrieval Relevance Results
        if 'retrieval_relevance' in results:
            report.append("RETRIEVAL RELEVANCE EVALUATION")
            report.append("-" * 40)
            overall = results['retrieval_relevance']['overall']
            report.append(f"Overall Accuracy: {overall.accuracy:.3f}")
            if 'avg_relevance_score' in overall.additional_metrics:
                report.append(f"Average Relevance Score: {overall.additional_metrics['avg_relevance_score']:.3f}")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report) 