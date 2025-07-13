// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Supported file types
export const SUPPORTED_FILE_TYPES = [
  '.pdf',
  '.docx', 
  '.txt',
  '.html',
  '.csv',
  '.json'
];

export const SUPPORTED_FILE_EXTENSIONS = SUPPORTED_FILE_TYPES.map(ext => ext.slice(1));

// File size limits
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const MAX_FILES_PER_UPLOAD = 10;

// Search configuration
export const DEFAULT_SEARCH_TOP_K = 10;
export const MAX_SEARCH_TOP_K = 50;

// Graph visualization
export const GRAPH_NODE_RADIUS = 20;
export const GRAPH_ANIMATION_DURATION = 300;

// UI Configuration
export const TOAST_DURATION = 5000; // 5 seconds
export const DEBOUNCE_DELAY = 300; // 300ms

// Local storage keys
export const STORAGE_KEYS = {
  DOCUMENTS: 'uploadedDocuments',
  QUERY_HISTORY: 'queryHistory',
  USER_PREFERENCES: 'userPreferences',
  THEME: 'theme',
} as const;

// Search types
export const SEARCH_TYPES = {
  VECTOR: 'vector',
  GRAPH: 'graph', 
  KEYWORD: 'keyword',
  HYBRID: 'hybrid',
} as const;

// Document domains
export const DOMAINS = {
  GENERAL: 'general',
  TECHNICAL: 'technical',
  AUTOMOTIVE: 'automotive',
  MEDICAL: 'medical',
  LEGAL: 'legal',
} as const;

// Status types
export const STATUS_TYPES = {
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UPLOAD_FAILED: 'Upload failed. Please try again.',
  SEARCH_FAILED: 'Search failed. Please try again.',
  GRAPH_LOAD_FAILED: 'Failed to load graph data.',
  INVALID_FILE_TYPE: 'Invalid file type. Please select a supported file.',
  FILE_TOO_LARGE: 'File is too large. Maximum size is 50MB.',
  TOO_MANY_FILES: 'Too many files. Maximum is 10 files per upload.',
} as const;

// Success messages
export const SUCCESS_MESSAGES = {
  UPLOAD_SUCCESS: 'Documents uploaded successfully!',
  SEARCH_SUCCESS: 'Search completed successfully!',
  DELETE_SUCCESS: 'Document deleted successfully!',
  CLEAR_SUCCESS: 'All documents cleared successfully!',
} as const; 