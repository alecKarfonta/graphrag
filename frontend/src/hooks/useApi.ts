// TODO: Uncomment when dependencies are installed
/*
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, ApiError } from '../services/api';
import { Document, QueryResult, GraphData, SearchOptions } from '../types/api';
import { toast } from 'react-hot-toast';

// Query keys for React Query
export const queryKeys = {
  health: ['health'],
  documents: ['documents'],
  graph: ['graph'],
  graphStats: ['graphStats'],
  supportedFormats: ['supportedFormats'],
} as const;

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
    retryDelay: 1000,
  });
};

// Documents hooks
export const useDocuments = () => {
  return useQuery({
    queryKey: queryKeys.documents,
    queryFn: () => apiClient.getDocuments(),
    refetchInterval: 10000, // Refetch every 10 seconds
  });
};

export const useUploadDocuments = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ files, domain, buildKnowledgeGraph }: {
      files: File[];
      domain?: string;
      buildKnowledgeGraph?: boolean;
    }) => apiClient.uploadDocuments(files, domain, buildKnowledgeGraph),
    onSuccess: () => {
      toast.success('Documents uploaded successfully!');
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      queryClient.invalidateQueries({ queryKey: queryKeys.graph });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || 'Upload failed');
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (documentName: string) => apiClient.deleteDocument(documentName),
    onSuccess: () => {
      toast.success('Document deleted successfully!');
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      queryClient.invalidateQueries({ queryKey: queryKeys.graph });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || 'Delete failed');
    },
  });
};

export const useClearAllDocuments = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiClient.clearAllDocuments(),
    onSuccess: () => {
      toast.success('All documents cleared successfully!');
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      queryClient.invalidateQueries({ queryKey: queryKeys.graph });
    },
    onError: (error: ApiError) => {
      toast.error(error.message || 'Clear failed');
    },
  });
};

// Search hooks
export const useSearch = () => {
  return useMutation({
    mutationFn: ({ query, topK }: { query: string; topK?: number }) =>
      apiClient.search(query, topK),
    onError: (error: ApiError) => {
      toast.error(error.message || 'Search failed');
    },
  });
};

export const useAdvancedSearch = () => {
  return useMutation({
    mutationFn: (options: SearchOptions) => apiClient.advancedSearch(options),
    onError: (error: ApiError) => {
      toast.error(error.message || 'Advanced search failed');
    },
  });
};

// Graph hooks
export const useGraphData = () => {
  return useQuery({
    queryKey: queryKeys.graph,
    queryFn: () => apiClient.getGraphData(),
    refetchInterval: 15000, // Refetch every 15 seconds
    retry: 3,
    retryDelay: 2000,
  });
};

export const useGraphStats = () => {
  return useQuery({
    queryKey: queryKeys.graphStats,
    queryFn: () => apiClient.getGraphStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Utility hooks
export const useSupportedFormats = () => {
  return useQuery({
    queryKey: queryKeys.supportedFormats,
    queryFn: () => apiClient.getSupportedFormats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Custom hook for API connection status
export const useApiConnection = () => {
  const healthQuery = useHealthCheck();
  
  return {
    isConnected: healthQuery.isSuccess && healthQuery.data?.status === 'healthy',
    isLoading: healthQuery.isLoading,
    error: healthQuery.error,
    refetch: healthQuery.refetch,
  };
};
*/

// Placeholder exports for now
export const queryKeys = {
  health: ['health'],
  documents: ['documents'],
  graph: ['graph'],
  graphStats: ['graphStats'],
  supportedFormats: ['supportedFormats'],
} as const;

// Placeholder hooks that will be implemented when dependencies are installed
export const useHealthCheck = () => ({
  data: null,
  isLoading: false,
  error: null,
  refetch: () => {},
});

export const useDocuments = () => ({
  data: null,
  isLoading: false,
  error: null,
});

export const useUploadDocuments = () => ({
  mutate: () => {},
  isLoading: false,
  error: null,
});

export const useDeleteDocument = () => ({
  mutate: () => {},
  isLoading: false,
  error: null,
});

export const useClearAllDocuments = () => ({
  mutate: () => {},
  isLoading: false,
  error: null,
});

export const useSearch = () => ({
  mutate: () => {},
  isLoading: false,
  error: null,
});

export const useAdvancedSearch = () => ({
  mutate: () => {},
  isLoading: false,
  error: null,
});

export const useGraphData = () => ({
  data: null,
  isLoading: false,
  error: null,
});

export const useGraphStats = () => ({
  data: null,
  isLoading: false,
  error: null,
});

export const useSupportedFormats = () => ({
  data: null,
  isLoading: false,
  error: null,
});

export const useApiConnection = () => ({
  isConnected: false,
  isLoading: false,
  error: null,
  refetch: () => {},
}); 