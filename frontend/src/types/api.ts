// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
  timestamp?: string;
}

// Document Types
export interface Document {
  id: string;
  name: string;
  type: string;
  status: 'processing' | 'completed' | 'error';
  uploadedAt: string;
  chunks?: number;
  entities?: number;
  relationships?: number;
  size?: number;
  lastModified?: string;
}

export interface DocumentChunk {
  chunk_id: string;
  text: string;
  source_file: string;
  page_number?: number;
  section_header?: string;
  chunk_index: number;
  metadata: Record<string, any>;
}

export interface DocumentProcessingResult {
  filename: string;
  chunks: DocumentChunk[];
  total_chunks: number;
  entities?: number;
  relationships?: number;
  use_semantic_chunking?: boolean;
}

export interface DocumentBatchResult {
  results: Record<string, DocumentProcessingResult>;
  total_files: number;
  domain?: string;
  build_knowledge_graph?: boolean;
}

// Query Types
export interface QueryResult {
  answer: string;
  results: SearchResult[];
  total_results: number;
  search_type: string;
  query_analysis: QueryAnalysis;
  sources?: string[];
}

export interface SearchResult {
  content: string;
  source: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface QueryAnalysis {
  query: string;
  intent: QueryIntent | string;
  entities: QueryEntity[] | string[];
  expansion?: QueryExpansion;
  reasoning_path?: ReasoningPath;
  llm_analysis?: any;
}

export interface QueryIntent {
  primary_intent: string;
  confidence: number;
  reasoning_type?: string;
}

export interface QueryEntity {
  name: string;
  entity_type?: string;
  confidence: number;
  context?: string;
}

export interface QueryExpansion {
  original_query: string;
  expanded_terms: string[];
  reasoning?: string;
}

export interface ReasoningPath {
  steps: string[];
  entities_involved: string[];
  expected_outcome: string;
  confidence: number;
}

// Graph Types
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: GraphStats;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
  size?: number;
  color?: string;
  occurrence?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
  weight?: number;
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
  edge_types: Record<string, number>;
  domains: Record<string, number>;
}

// Upload Types
export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

export interface SupportedFormats {
  supported_formats: string[];
  features: {
    semantic_chunking: boolean;
    metadata_extraction: boolean;
    content_type_classification: boolean;
    structure_preservation: boolean;
  };
}

// Health Check Types
export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services?: {
    api: boolean;
    vector_store: boolean;
    knowledge_graph: boolean;
  };
}

// Clear/Delete Types
export interface ClearResult {
  message: string;
  vector_store_cleared: boolean;
  knowledge_graph_cleared: boolean;
}

export interface DeleteDocumentResult {
  message: string;
  removed_from_vector_store: boolean;
  removed_from_knowledge_graph: boolean;
}

export interface DocumentListResult {
  documents: string[];
  total_documents: number;
  vector_store_documents: number;
  knowledge_graph_documents: number;
}

export interface UploadResponse {
  message: string;
  documents: Document[];
  processing_status: 'started' | 'completed' | 'error';
}

export interface SystemStats {
  total_documents: number;
  total_entities: number;
  total_relationships: number;
  graph_size: number;
  last_updated: string;
}

export interface SupportedFormat {
  extension: string;
  mime_type: string;
  description: string;
  max_size?: number;
}

export interface SearchOptions {
  query: string;
  search_type: 'vector' | 'graph' | 'keyword' | 'hybrid';
  top_k: number;
  domain?: string;
  filters?: Record<string, any>;
} 