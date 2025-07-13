import { SUPPORTED_FILE_EXTENSIONS, MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD } from './constants';

// File validation helpers
export const isValidFileType = (file: File): boolean => {
  const extension = file.name.split('.').pop()?.toLowerCase();
  return extension ? SUPPORTED_FILE_EXTENSIONS.includes(extension) : false;
};

export const isValidFileSize = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE;
};

export const isValidFileCount = (files: File[]): boolean => {
  return files.length <= MAX_FILES_PER_UPLOAD;
};

export const validateFiles = (files: File[]): { valid: File[]; errors: string[] } => {
  const valid: File[] = [];
  const errors: string[] = [];

  if (files.length > MAX_FILES_PER_UPLOAD) {
    errors.push(`Too many files. Maximum is ${MAX_FILES_PER_UPLOAD} files per upload.`);
    return { valid, errors };
  }

  files.forEach(file => {
    if (!isValidFileType(file)) {
      errors.push(`${file.name}: Invalid file type. Supported types: ${SUPPORTED_FILE_EXTENSIONS.join(', ')}`);
    } else if (!isValidFileSize(file)) {
      errors.push(`${file.name}: File is too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}`);
    } else {
      valid.push(file);
    }
  });

  return { valid, errors };
};

// File size formatting
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Date formatting
export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatDateTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
  
  return formatDate(dateObj);
};

// String helpers
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const sanitizeFileName = (fileName: string): string => {
  return fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
};

// Array helpers
export const chunkArray = <T>(array: T[], size: number): T[][] => {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

export const uniqueArray = <T>(array: T[]): T[] => {
  return [...new Set(array)];
};

// Object helpers
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

// URL helpers
export const getFileExtension = (fileName: string): string => {
  return fileName.split('.').pop()?.toLowerCase() || '';
};

export const getFileIcon = (fileName: string): string => {
  const extension = getFileExtension(fileName);
  
  switch (extension) {
    case 'pdf':
      return '📄';
    case 'docx':
    case 'doc':
      return '📝';
    case 'txt':
      return '📋';
    case 'html':
    case 'htm':
      return '🌐';
    case 'csv':
      return '📊';
    case 'json':
      return '📋';
    default:
      return '📄';
  }
};

// Color helpers
export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'text-success-500 bg-success-50 border-success-200';
    case 'processing':
      return 'text-warning-500 bg-warning-50 border-warning-200';
    case 'error':
      return 'text-error-500 bg-error-50 border-error-200';
    default:
      return 'text-gray-500 bg-gray-50 border-gray-200';
  }
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-success-500';
  if (confidence >= 0.6) return 'text-warning-500';
  return 'text-error-500';
};

// Debounce helper
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Local storage helpers
export const getFromStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error reading from localStorage key "${key}":`, error);
    return defaultValue;
  }
};

export const setToStorage = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error writing to localStorage key "${key}":`, error);
  }
};

export const removeFromStorage = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Error removing from localStorage key "${key}":`, error);
  }
}; 