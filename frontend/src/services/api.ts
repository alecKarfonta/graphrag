import { 
  Document, 
  QueryResult, 
  GraphData, 
  SupportedFormats, 
  HealthStatus,
  ClearResult,
  DeleteDocumentResult,
  DocumentListResult,
  SearchOptions,
  UploadResponse,
  SystemStats,
  SupportedFormat
} from '../types/api';

const getApiBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // In development, use the browser's hostname and port 8000
  // In production, this will need to be configured via environment variables
  // or a reverse proxy. For now, we can default to the development-style URL
  // but use the window's hostname.
  return `http://${window.location.hostname}:8000`;
};

// API Configuration
const API_BASE_URL = getApiBaseUrl();

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// API client class
class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorDetails;
        
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
          errorDetails = errorData;
        } catch {
          // If error response is not JSON, use default message
        }
        
        throw new ApiError(errorMessage, response.status, errorDetails);
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return {} as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error',
        0
      );
    }
  }

  // Health check
  async healthCheck(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health');
  }

  // Document operations
  async uploadDocuments(
    files: File[],
    domain: string = 'general',
    buildKnowledgeGraph: boolean = true
  ): Promise<Record<string, any>> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    return this.request<Record<string, any>>(
      `/ingest-documents?domain=${domain}&build_knowledge_graph=${buildKnowledgeGraph}`,
      {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      }
    );
  }

  async getDocuments(): Promise<DocumentListResult> {
    return this.request<DocumentListResult>('/documents/list');
  }

  async deleteDocument(documentName: string): Promise<DeleteDocumentResult> {
    return this.request<DeleteDocumentResult>(
      `/documents/${encodeURIComponent(documentName)}`,
      { method: 'DELETE' }
    );
  }

  async clearAllDocuments(): Promise<ClearResult> {
    return this.request<ClearResult>('/clear-all', { method: 'DELETE' });
  }

  // Query operations
  async search(query: string, topK: number = 10): Promise<QueryResult> {
    const formData = new URLSearchParams({
      query,
      top_k: topK.toString(),
    });

    return this.request<QueryResult>('/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
  }

  async advancedSearch(options: SearchOptions): Promise<QueryResult> {
    const formData = new URLSearchParams({
      query: options.query,
      search_type: options.search_type,
      top_k: options.top_k.toString(),
      ...(options.domain && { domain: options.domain }),
    });

    return this.request<QueryResult>('/search-advanced', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
  }

  // Graph operations
  async getGraphData(domain?: string): Promise<GraphData> {
    const params = domain ? `&domain=${encodeURIComponent(domain)}` : '';
    return this.request<GraphData>(`/knowledge-graph/export?format=json${params}`);
  }

  async getFilteredGraphData(filters: {
    domain?: string;
    max_entities?: number;
    max_relationships?: number;
    min_occurrence?: number;
    min_confidence?: number;
    entity_types?: string[];
    relationship_types?: string[];
    sort_by?: string;
    sort_order?: string;
  }): Promise<any> {
    return this.request<any>('/knowledge-graph/filtered', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  async getTopEntities(params: {
    domain?: string;
    limit?: number;
    min_occurrence?: number;
    entity_type?: string;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params.domain) queryParams.append('domain', params.domain);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_occurrence) queryParams.append('min_occurrence', params.min_occurrence.toString());
    if (params.entity_type) queryParams.append('entity_type', params.entity_type);
    
    return this.request<any>(`/knowledge-graph/top-entities?${queryParams.toString()}`);
  }

  async getTopRelationships(params: {
    domain?: string;
    limit?: number;
    min_weight?: number;
    relationship_type?: string;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params.domain) queryParams.append('domain', params.domain);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_weight) queryParams.append('min_weight', params.min_weight.toString());
    if (params.relationship_type) queryParams.append('relationship_type', params.relationship_type);
    
    return this.request<any>(`/knowledge-graph/top-relationships?${queryParams.toString()}`);
  }

  async getGraphStats(domain?: string): Promise<any> {
    const params = domain ? `?domain=${encodeURIComponent(domain)}` : '';
    return this.request<any>(`/knowledge-graph/stats${params}`);
  }

  async getAvailableDomains(): Promise<{ domains: string[]; count: number }> {
    return this.request<{ domains: string[]; count: number }>('/knowledge-graph/domains');
  }

  async getDomainStatistics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/knowledge-graph/domain-stats');
  }

  // Utility operations
  async getSupportedFormats(): Promise<SupportedFormats> {
    return this.request<SupportedFormats>('/supported-formats');
  }

  // Process single document (for testing)
  async processDocument(
    file: File,
    useSemanticChunking: boolean = true
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<any>(
      `/process-document?use_semantic_chunking=${useSemanticChunking}`,
      {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      }
    );
  }

  async processDocumentsBatch(
    files: File[],
    useSemanticChunking: boolean = true
  ): Promise<any> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    return this.request<any>(
      `/process-documents-batch?use_semantic_chunking=${useSemanticChunking}`,
      {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      }
    );
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

class ApiService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  // Document management
  async uploadDocuments(
    files: File[], 
    domain: string = 'general', 
    buildKnowledgeGraph: boolean = true
  ): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/ingest-documents?domain=${domain}&build_knowledge_graph=${buildKnowledgeGraph}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  }

  async getDocuments(): Promise<Document[]> {
    return this.request<Document[]>('/documents/list');
  }

  async deleteDocument(name: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/documents/${name}`, {
      method: 'DELETE',
    });
  }

  async getSupportedFormats(): Promise<SupportedFormat[]> {
    const response = await this.request<SupportedFormats>('/supported-formats');
    
    // Convert the backend response to the expected format
    const formatMap: { [key: string]: { mime_type: string; description: string } } = {
      '.pdf': { mime_type: 'application/pdf', description: 'Portable Document Format' },
      '.docx': { mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', description: 'Microsoft Word Document' },
      '.txt': { mime_type: 'text/plain', description: 'Plain Text File' },
      '.html': { mime_type: 'text/html', description: 'HyperText Markup Language' },
      '.csv': { mime_type: 'text/csv', description: 'Comma-Separated Values' },
      '.json': { mime_type: 'application/json', description: 'JavaScript Object Notation' },
    };

    return response.supported_formats.map(extension => ({
      extension,
      mime_type: formatMap[extension]?.mime_type || 'application/octet-stream',
      description: formatMap[extension]?.description || 'Unknown format',
      max_size: 50 * 1024 * 1024 // 50MB default
    }));
  }

  // Query operations
  async search(query: string, options?: Partial<SearchOptions>): Promise<QueryResult> {
    const searchOptions: SearchOptions = {
      query,
      search_type: 'hybrid',
      top_k: 10,
      ...options,
    };

    return this.request<QueryResult>('/search', {
      method: 'POST',
      body: JSON.stringify(searchOptions),
    });
  }

  async advancedSearch(options: SearchOptions): Promise<QueryResult> {
    return this.request<QueryResult>('/search-advanced', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  // Graph operations
  async getGraphData(domain?: string): Promise<GraphData> {
    const params = domain ? `?domain=${encodeURIComponent(domain)}` : '';
    return this.request<GraphData>(`/knowledge-graph/export${params}`);
  }

  async getFilteredGraphData(filters: {
    domain?: string;
    max_entities?: number;
    max_relationships?: number;
    min_occurrence?: number;
    min_confidence?: number;
    entity_types?: string[];
    relationship_types?: string[];
    sort_by?: string;
    sort_order?: string;
  }): Promise<any> {
    return this.request<any>('/knowledge-graph/filtered', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  async getTopEntities(params: {
    domain?: string;
    limit?: number;
    min_occurrence?: number;
    entity_type?: string;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params.domain) queryParams.append('domain', params.domain);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_occurrence) queryParams.append('min_occurrence', params.min_occurrence.toString());
    if (params.entity_type) queryParams.append('entity_type', params.entity_type);
    
    return this.request<any>(`/knowledge-graph/top-entities?${queryParams.toString()}`);
  }

  async getTopRelationships(params: {
    domain?: string;
    limit?: number;
    min_weight?: number;
    relationship_type?: string;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params.domain) queryParams.append('domain', params.domain);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_weight) queryParams.append('min_weight', params.min_weight.toString());
    if (params.relationship_type) queryParams.append('relationship_type', params.relationship_type);
    
    return this.request<any>(`/knowledge-graph/top-relationships?${queryParams.toString()}`);
  }

  async getGraphStats(domain?: string): Promise<SystemStats> {
    const params = domain ? `?domain=${encodeURIComponent(domain)}` : '';
    return this.request<SystemStats>(`/knowledge-graph/stats${params}`);
  }

  async getAvailableDomains(): Promise<{ domains: string[]; count: number }> {
    return this.request<{ domains: string[]; count: number }>('/knowledge-graph/domains');
  }

  async getDomainStatistics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/knowledge-graph/domain-stats');
  }

  // System operations
  async clearAllData(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/clear-all', {
      method: 'DELETE',
    });
  }

  // Utility methods
  async isConnected(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
export default apiService; 