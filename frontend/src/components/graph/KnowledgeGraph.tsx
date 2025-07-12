import React, { useState, useEffect, useCallback } from 'react';
import { GraphData, GraphNode, GraphEdge, SystemStats } from '../../types/api';
import type { GraphStats as GraphStatsType } from '../../types/api';
import apiService from '../../services/api';
import GraphVisualization from './GraphVisualization';
import GraphControls from './GraphControls';
import GraphStatsComponent from './GraphStats';
import GraphFilterControls, { GraphFilters } from './GraphFilterControls';

const KnowledgeGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [selectedNodeType, setSelectedNodeType] = useState<string | null>(null);
  const [selectedEdgeType, setSelectedEdgeType] = useState<string | null>(null);
  const [layout, setLayout] = useState<'force' | 'circular' | 'hierarchical'>('force');
  const [showLabels, setShowLabels] = useState(true);
  const [nodeSize, setNodeSize] = useState(8);
  const [linkDistance, setLinkDistance] = useState(100);
  const [activeTab, setActiveTab] = useState<'visualization' | 'stats' | 'controls' | 'filters'>('visualization');
  
  // Domain filtering state
  const [availableDomains, setAvailableDomains] = useState<string[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [domainStats, setDomainStats] = useState<Record<string, any>>({});

  // Filtering state
  const [currentFilters, setCurrentFilters] = useState<GraphFilters>({
    max_entities: 500,
    max_relationships: 500,
    min_occurrence: 1,
    min_confidence: 0.0,
    entity_types: [],
    relationship_types: [],
    sort_by: 'occurrence',
    sort_order: 'desc'
  });
  const [filteredData, setFilteredData] = useState<GraphData | null>(null);
  const [filterLoading, setFilterLoading] = useState(false);

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [domainsResult, domainStatsResult] = await Promise.all([
          apiService.getAvailableDomains(),
          apiService.getDomainStatistics(),
        ]);
        setAvailableDomains(domainsResult.domains);
        setDomainStats(domainStatsResult);

        const [graphDataResult, statsResult] = await Promise.all([
          apiService.getGraphData(selectedDomain || undefined),
          apiService.getGraphStats(selectedDomain || undefined),
        ]);
        setGraphData(graphDataResult);
        setSystemStats(statsResult);
      } catch (err) {
        console.error('Failed to load initial data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, [selectedDomain]);

  // Handle filter changes
  const handleFiltersChange = useCallback(async (filters: GraphFilters) => {
    setCurrentFilters(filters);
    setFilterLoading(true);
    try {
      const filtersWithDomain = {
        ...filters,
        domain: selectedDomain || undefined
      };
      const filteredResult = await apiService.getFilteredGraphData(filtersWithDomain);
      setFilteredData(filteredResult.filtered_data);
    } catch (err) {
      console.error('Failed to apply filters:', err);
      setError(err instanceof Error ? err.message : 'Failed to apply filters');
    } finally {
      setFilterLoading(false);
    }
  }, [selectedDomain]);

  // Handle filter reset
  const handleFilterReset = useCallback(() => {
    const defaultFilters = {
      max_entities: 500,
      max_relationships: 500,
      min_occurrence: 1,
      min_confidence: 0.0,
      entity_types: [],
      relationship_types: [],
      sort_by: 'occurrence',
      sort_order: 'desc'
    };
    setCurrentFilters(defaultFilters);
    setFilteredData(null); // Clear filtered data to show the original graph
  }, []);

  // Handle domain selection
  const handleDomainChange = useCallback((domain: string | null) => {
    setSelectedDomain(domain);
    setSelectedNode(null);
    setSelectedEdge(null);
    setSelectedNodeType(null);
    setSelectedEdgeType(null);
  }, []);

  // Use filtered data if available, otherwise use original data
  const displayData = filteredData || graphData;

  // Filter nodes and edges based on selected types
  const nodesToRender = (displayData?.nodes || []).filter(node => 
    !selectedNodeType || node.type === selectedNodeType
  );

  const edgesToRender = (displayData?.edges || []).filter(edge => 
    !selectedEdgeType || edge.type === selectedEdgeType
  );

  // Create filtered graph data
  const finalGraphData: GraphData | null = displayData ? {
    ...displayData,
    nodes: nodesToRender,
    edges: edgesToRender
  } : null;

  // Handle node selection
  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  // Handle edge selection
  const handleEdgeClick = useCallback((edge: GraphEdge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  // Reset all filters
  const handleResetFilters = useCallback(() => {
    setSelectedNodeType(null);
    setSelectedEdgeType(null);
    setSelectedNode(null);
    setSelectedEdge(null);
  }, []);

  // Refresh data
  const handleRefresh = useCallback(() => {
    // Re-trigger the initial data load
    // This is a bit of a trick, but it's effective.
    // A more robust solution might involve a dedicated "refresh" state.
    setSelectedDomain(prev => (prev === null ? '' : null));
    // Reset back to null if it was an empty string, to trigger the effect again
    if (selectedDomain === '') setSelectedDomain(null);
  }, [selectedDomain]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Knowledge Graph
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Interactive visualization of your knowledge graph.
          </p>
        </div>
        
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-3">
            <svg className="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-lg text-gray-600 dark:text-gray-400">Loading knowledge graph...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Knowledge Graph
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Interactive visualization of your knowledge graph.
          </p>
        </div>
        
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Error Loading Graph
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                {error}
              </div>
              <div className="mt-4">
                <button
                  onClick={handleRefresh}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!displayData || !systemStats) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Knowledge Graph
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Interactive visualization of your knowledge graph.
          </p>
        </div>
        
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                No Graph Data Available
              </h3>
              <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                Upload some documents to build your knowledge graph and see it visualized here.
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Knowledge Graph
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Interactive visualization of your knowledge graph with {displayData?.nodes?.length || 0} nodes and {displayData?.edges?.length || 0} relationships.
              {selectedDomain && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 ml-2">
                  Domain: {selectedDomain}
                </span>
              )}
              {filteredData && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 ml-2">
                  Filtered
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {/* Domain Filter */}
            {availableDomains.length > 0 && (
              <div className="flex items-center space-x-2">
                <label htmlFor="domain-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Domain:
                </label>
                <select
                  id="domain-select"
                  value={selectedDomain || ''}
                  onChange={(e) => handleDomainChange(e.target.value || null)}
                  className="block w-40 rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                >
                  <option value="">All Domains</option>
                  {availableDomains.map(domain => (
                    <option key={domain} value={domain}>
                      {domain} ({domainStats[domain]?.nodes || 0} nodes)
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <button
              onClick={handleRefresh}
              className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {(['visualization', 'stats', 'controls', 'filters'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'visualization' && (
          <div className="space-y-6">
            {/* Selected Node/Edge Info */}
            {(selectedNode || selectedEdge) && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
                  {selectedNode ? 'Selected Node' : 'Selected Edge'}
                </h4>
                {selectedNode && (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getNodeTypeColor(selectedNode.type) }}
                      />
                      <span className="font-medium text-blue-900 dark:text-blue-100">
                        {selectedNode.label}
                      </span>
                      <span className="text-sm text-blue-700 dark:text-blue-300">
                        ({selectedNode.type})
                      </span>
                    </div>
                    {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                      <div className="text-sm text-blue-700 dark:text-blue-300">
                        <strong>Properties:</strong> {Object.entries(selectedNode.properties).map(([key, value]) => `${key}: ${value}`).join(', ')}
                      </div>
                    )}
                  </div>
                )}
                {selectedEdge && (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-blue-900 dark:text-blue-100">
                        {selectedEdge.label}
                      </span>
                      <span className="text-sm text-blue-700 dark:text-blue-300">
                        ({selectedEdge.type})
                      </span>
                    </div>
                    <div className="text-sm text-blue-700 dark:text-blue-300">
                      <strong>From:</strong> {displayData?.nodes?.find(n => n.id === selectedEdge.source)?.label || selectedEdge.source} 
                      <strong className="ml-2">To:</strong> {displayData?.nodes?.find(n => n.id === selectedEdge.target)?.label || selectedEdge.target}
                    </div>
                    {selectedEdge.properties && Object.keys(selectedEdge.properties).length > 0 && (
                      <div className="text-sm text-blue-700 dark:text-blue-300">
                        <strong>Properties:</strong> {Object.entries(selectedEdge.properties).map(([key, value]) => `${key}: ${value}`).join(', ')}
                      </div>
                    )}
                  </div>
                )}
                <button
                  onClick={() => {
                    setSelectedNode(null);
                    setSelectedEdge(null);
                  }}
                  className="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                >
                  Clear Selection
                </button>
              </div>
            )}

            {/* Graph Visualization */}
            <div className="flex-grow bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              {finalGraphData && (
                <GraphVisualization
                  data={finalGraphData}
                  onNodeClick={handleNodeClick}
                  onEdgeClick={handleEdgeClick}
                  selectedNode={selectedNode?.id || null}
                  selectedEdge={selectedEdge?.id || null}
                  layout={layout}
                  showLabels={showLabels}
                  nodeSize={nodeSize}
                  linkDistance={linkDistance}
                />
              )}
            </div>
          </div>
        )}

        {activeTab === 'stats' && systemStats && (
          <div className="space-y-6">
            <GraphStatsComponent
              stats={displayData.stats}
              systemStats={systemStats}
              nodes={displayData.nodes}
              edges={displayData.edges}
            />
            
            {/* Domain Statistics */}
            {Object.keys(domainStats).length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Domain Statistics
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(domainStats).map(([domain, stats]) => (
                    <div 
                      key={domain}
                      className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
                        selectedDomain === domain
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }`}
                      onClick={() => handleDomainChange(selectedDomain === domain ? null : domain)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {domain}
                        </h4>
                        {selectedDomain === domain && (
                          <span className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-400 px-2 py-1 rounded">
                            Active
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                        <div>Nodes: {stats.nodes || 0}</div>
                        <div>Edges: {stats.edges || 0}</div>
                        {stats.density && (
                          <div>Density: {(stats.density * 100).toFixed(1)}%</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'controls' && (
          <GraphControls
            nodes={displayData.nodes}
            edges={displayData.edges}
            selectedNodeType={selectedNodeType}
            selectedEdgeType={selectedEdgeType}
            layout={layout}
            showLabels={showLabels}
            nodeSize={nodeSize}
            linkDistance={linkDistance}
            onNodeTypeChange={setSelectedNodeType}
            onEdgeTypeChange={setSelectedEdgeType}
            onLayoutChange={setLayout}
            onShowLabelsChange={setShowLabels}
            onNodeSizeChange={setNodeSize}
            onLinkDistanceChange={setLinkDistance}
            onResetFilters={handleResetFilters}
          />
        )}

        {activeTab === 'filters' && (
          <GraphFilterControls
            onFiltersChange={handleFiltersChange}
            onResetFilters={handleFilterReset}
            isLoading={filterLoading}
          />
        )}
      </div>
    </div>
  );
};

// Helper function to get node type color
const getNodeTypeColor = (type: string): string => {
  const colors: { [key: string]: string } = {
    'PERSON': '#3B82F6',
    'ORGANIZATION': '#8B5CF6',
    'LOCATION': '#10B981',
    'TECHNOLOGY': '#F59E0B',
    'CONCEPT': '#EF4444',
    'DATE': '#6B7280',
    'EVENT': '#EC4899',
    'FUNCTION': '#06B6D4',
    'CLASS': '#8B5CF6',
    'VARIABLE': '#10B981',
    'MODULE': '#F59E0B',
    'default': '#6B7280'
  };
  return colors[type] || colors.default;
};

export default KnowledgeGraph; 