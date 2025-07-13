import React, { useState, useCallback } from 'react';
import { Document, SupportedFormat } from '../../types/api';
import apiService from '../../services/api';
import { DOMAINS } from '../../utils/constants';

interface UploadProgress {
  [key: string]: {
    progress: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
    message?: string;
  };
}

const DocumentUpload: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
  const [isUploading, setIsUploading] = useState(false);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormat[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDomain, setSelectedDomain] = useState<string>(DOMAINS.GENERAL);
  const [availableDomains, setAvailableDomains] = useState<string[]>([]);
  const [customDomain, setCustomDomain] = useState<string>('');
  const [useCustomDomain, setUseCustomDomain] = useState<boolean>(false);

  // Load supported formats and available domains on component mount
  React.useEffect(() => {
    const loadData = async () => {
      try {
        // Load supported formats
        const formats = await apiService.getSupportedFormats();
        setSupportedFormats(formats);
        
        // Load available domains
        try {
          const domainsResponse = await apiService.getAvailableDomains();
          // Use default domains if API returns empty list or fails
          if (domainsResponse.domains && domainsResponse.domains.length > 0) {
            setAvailableDomains(domainsResponse.domains);
          } else {
            console.warn('Backend returned empty domains list, using default domains');
            setAvailableDomains(Object.values(DOMAINS));
          }
        } catch (err) {
          console.warn('Failed to load available domains:', err);
          // Use default domains if API fails
          setAvailableDomains(Object.values(DOMAINS));
        }
      } catch (err) {
        console.error('Failed to load data:', err);
      }
    };
    loadData();
  }, []);

  const validateFile = (file: File): string | null => {
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return `File ${file.name} is too large. Maximum size is 50MB.`;
    }

    const extension = file.name.split('.').pop()?.toLowerCase();
    
    // Check if supportedFormats is available and is an array
    if (!supportedFormats || !Array.isArray(supportedFormats) || supportedFormats.length === 0) {
      // If formats not loaded yet, allow common formats
      const commonFormats = ['.pdf', '.docx', '.txt', '.html', '.csv', '.json'];
      const isSupported = commonFormats.some(format => 
        format.toLowerCase() === `.${extension}`
      );
      
      if (!isSupported) {
        return `File type .${extension} is not supported.`;
      }
    } else {
      const isSupported = supportedFormats.some(format => 
        format.extension.toLowerCase() === `.${extension}`
      );

      if (!isSupported) {
        return `File type .${extension} is not supported.`;
      }
    }

    return null;
  };

  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles = Array.from(selectedFiles);
    const validFiles: File[] = [];
    const errors: string[] = [];

    newFiles.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      setError(errors.join('\n'));
      setTimeout(() => setError(null), 5000);
    }

    setFiles(prev => [...prev, ...validFiles]);
  }, [supportedFormats]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setError(null);

    // Determine which domain to use
    const domainToUse = useCustomDomain ? customDomain : selectedDomain;

    // Initialize progress for all files
    const initialProgress: UploadProgress = {};
    files.forEach(file => {
      initialProgress[file.name] = {
        progress: 0,
        status: 'uploading'
      };
    });
    setUploadProgress(initialProgress);

    try {
      const response = await apiService.uploadDocuments(files, domainToUse);
      
      // Update progress to completed
      const completedProgress: UploadProgress = {};
      files.forEach(file => {
        completedProgress[file.name] = {
          progress: 100,
          status: 'completed',
          message: 'Upload successful'
        };
      });
      setUploadProgress(completedProgress);

      // Clear files after successful upload
      setTimeout(() => {
        setFiles([]);
        setUploadProgress({});
        // Reset custom domain after successful upload
        if (useCustomDomain) {
          setCustomDomain('');
          setUseCustomDomain(false);
        }
      }, 2000);

    } catch (err) {
      console.error('Upload failed:', err);
      setError(err instanceof Error ? err.message : 'Upload failed');
      
      // Update progress to error
      const errorProgress: UploadProgress = {};
      files.forEach(file => {
        errorProgress[file.name] = {
          progress: 0,
          status: 'error',
          message: 'Upload failed'
        };
      });
      setUploadProgress(errorProgress);
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Document Upload
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Upload documents to build your knowledge graph. Supported formats: PDF, DOCX, TXT, and more.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Upload Error
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Domain Selection */}
      <div className="space-y-4">
        <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
            Document Domain
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Select a domain to categorize your documents. This helps organize the knowledge graph and enables domain-specific filtering.
          </p>
          
          {/* Domain Selection Options */}
          <div className="space-y-4">
            {/* Existing Domains */}
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Select from existing domains:
              </label>
              <div className="flex items-center space-x-4">
                <select
                  id="domain-select"
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="block w-64 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                  disabled={isUploading || useCustomDomain}
                >
                  {availableDomains.map((domain) => (
                    <option key={domain} value={domain}>
                      {domain.charAt(0).toUpperCase() + domain.slice(1)}
                    </option>
                  ))}
                </select>
                
                <button
                  type="button"
                  onClick={() => {
                    setUseCustomDomain(false);
                    setCustomDomain('');
                  }}
                  disabled={isUploading}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                    !useCustomDomain
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  Use Existing
                </button>
              </div>
            </div>

            {/* Custom Domain */}
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Or enter a custom domain:
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="text"
                  value={customDomain}
                  onChange={(e) => setCustomDomain(e.target.value)}
                  placeholder="Enter custom domain name..."
                  className="block w-64 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                  disabled={isUploading || !useCustomDomain}
                />
                
                <button
                  type="button"
                  onClick={() => {
                    setUseCustomDomain(true);
                    setCustomDomain('');
                  }}
                  disabled={isUploading}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                    useCustomDomain
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  Use Custom
                </button>
              </div>
              
              {useCustomDomain && (
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  <p>• Custom domains will be created automatically</p>
                  <p>• Use lowercase letters, numbers, and hyphens only</p>
                  <p>• Examples: "finance", "research", "product-development"</p>
                </div>
              )}
            </div>
          </div>
          
          {/* Current Selection Display */}
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              Selected Domain:
            </p>
            <p className="text-lg font-semibold text-primary-600 dark:text-primary-400">
              {useCustomDomain ? (customDomain || 'Enter custom domain...') : selectedDomain}
            </p>
          </div>
          
          <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
            <p>Available existing domains: {availableDomains.length}</p>
            {availableDomains.length > 0 && (
              <p className="mt-1">
                Sample: {availableDomains.slice(0, 3).join(', ')}
                {availableDomains.length > 3 && '...'}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
          isDragOver
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="mx-auto w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Upload documents to start building your knowledge graph
            </p>
          </div>

          <input
            type="file"
            multiple
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
            id="file-upload"
            accept={supportedFormats.map(f => f.extension).join(',')}
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 cursor-pointer"
          >
            Choose Files
          </label>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Selected Files ({files.length})
            </h3>
            <button
              onClick={uploadFiles}
              disabled={isUploading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading...
                </>
              ) : (
                'Upload Files'
              )}
            </button>
          </div>

          <div className="space-y-3">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {uploadProgress[file.name] && (
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            uploadProgress[file.name].status === 'error'
                              ? 'bg-red-500'
                              : uploadProgress[file.name].status === 'completed'
                              ? 'bg-green-500'
                              : 'bg-primary-500'
                          }`}
                          style={{ width: `${uploadProgress[file.name].progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {uploadProgress[file.name].progress}%
                      </span>
                    </div>
                  )}
                  
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    disabled={isUploading}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Supported Formats */}
      {supportedFormats && supportedFormats.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Supported File Formats
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {supportedFormats.map((format) => (
              <div key={format.extension} className="text-xs text-gray-600 dark:text-gray-400">
                {format.extension} - {format.description}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload; 