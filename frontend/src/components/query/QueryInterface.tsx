import React, { useState } from 'react';
import { QueryResult, SearchOptions } from '../../types/api';
import apiService from '../../services/api';

const QueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'vector' | 'graph' | 'keyword' | 'hybrid'>('hybrid');
  const [topK, setTopK] = useState(10);
  const [domain, setDomain] = useState('');
  const [results, setResults] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const searchTypes = [
    { value: 'hybrid', label: 'Hybrid Search', description: 'Combines vector, graph, and keyword search' },
    { value: 'vector', label: 'Vector Search', description: 'Semantic similarity search' },
    { value: 'graph', label: 'Graph Search', description: 'Knowledge graph traversal' },
    { value: 'keyword', label: 'Keyword Search', description: 'Traditional text search' },
  ];

  const domains = [
    { value: '', label: 'All Domains' },
    { value: 'general', label: 'General' },
    { value: 'technical', label: 'Technical' },
    { value: 'automotive', label: 'Automotive' },
    { value: 'medical', label: 'Medical' },
    { value: 'legal', label: 'Legal' },
  ];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    // Add to query history
    if (!queryHistory.includes(query)) {
      setQueryHistory(prev => [query, ...prev.slice(0, 9)]);
    }

    try {
      const searchOptions: SearchOptions = {
        query: query.trim(),
        search_type: searchType,
        top_k: topK,
        domain: domain || undefined,
      };

      const result = await apiService.advancedSearch(searchOptions);
      setResults(result);
    } catch (err) {
      console.error('Search failed:', err);
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const selectHistoryItem = (historyQuery: string) => {
    setQuery(historyQuery);
  };

  const clearResults = () => {
    setResults(null);
    setError(null);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400';
    if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getEntityTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'PERSON': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      'ORGANIZATION': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      'LOCATION': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      'DATE': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      'TECHNOLOGY': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Query Interface
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Search your knowledge graph using advanced query strategies.
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="space-y-4">
          {/* Query Input */}
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Query
            </label>
            <div className="relative">
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your question or search query..."
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white resize-none"
                rows={3}
              />
              <div className="absolute bottom-2 right-2">
                <button
                  onClick={handleSearch}
                  disabled={loading || !query.trim()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Searching...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      Search
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Search Options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search Type */}
            <div>
              <label htmlFor="searchType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Type
              </label>
              <select
                id="searchType"
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              >
                {searchTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Top K Results */}
            <div>
              <label htmlFor="topK" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Results
              </label>
              <select
                id="topK"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={50}>50 results</option>
              </select>
            </div>

            {/* Domain */}
            <div>
              <label htmlFor="domain" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Domain
              </label>
              <select
                id="domain"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              >
                {domains.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Type Descriptions */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
              Search Strategy
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {searchTypes.map((type) => (
                <div key={type.value} className="flex items-start space-x-2">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    searchType === type.value ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'
                  }`} />
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">{type.label}</span>
                    <p className="text-gray-600 dark:text-gray-400">{type.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Query History */}
      {queryHistory.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Recent Queries
          </h3>
          <div className="flex flex-wrap gap-2">
            {queryHistory.map((historyQuery, index) => (
              <button
                key={index}
                onClick={() => selectHistoryItem(historyQuery)}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                {historyQuery}
              </button>
            ))}
          </div>
        </div>
      )}

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
                Search Error
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Search Results
            </h3>
            <button
              onClick={clearResults}
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            >
              Clear Results
            </button>
          </div>

          {/* LLM Answer */}
          <div className="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-lg border border-gray-300 dark:border-gray-700 p-6">
            <div className="flex items-start space-x-3 mb-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  AI Answer
                </h4>
                <div className="prose max-w-none">
                  <p className="text-gray-700 dark:text-gray-100 leading-relaxed whitespace-pre-wrap">
                    {results.answer}
                  </p>
                </div>
                <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>Search Type: {results.search_type}</span>
                  {results.total_results && <span>Total Results: {results.total_results}</span>}
                  {results.sources && results.sources.length > 0 && (
                    <span>Sources: {results.sources.length} documents</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Search Results */}
          {results.results && results.results.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Search Results ({results.results.length})
              </h4>
              <div className="space-y-3">
                {results.results.map((result: any, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-400">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">{result.content}</p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>Source: {result.source}</span>
                        <span>Score: {(result.score * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Query Analysis */}
          {results.query_analysis && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Query Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Intent</h5>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {typeof results.query_analysis.intent === 'object' 
                      ? results.query_analysis.intent.primary_intent 
                      : results.query_analysis.intent || 'Unknown'}
                  </p>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Keywords</h5>
                  <div className="flex flex-wrap gap-1">
                    {results.query_analysis.expansion?.expanded_terms?.map((keyword: string, index: number) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {keyword}
                      </span>
                    )) || (
                      <span className="text-xs text-gray-500 dark:text-gray-400">No keywords available</span>
                    )}
                  </div>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Entities</h5>
                  <div className="flex flex-wrap gap-1">
                    {results.query_analysis.entities?.map((entity: any, index: number) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                        {typeof entity === 'object' ? entity.name : entity}
                      </span>
                    )) || (
                      <span className="text-xs text-gray-500 dark:text-gray-400">No entities found</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QueryInterface; 