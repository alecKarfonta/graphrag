import React from 'react';
import { GraphNode, GraphEdge } from '../../types/api';
import type { GraphStats as GraphStatsType, SystemStats } from '../../types/api';

interface GraphStatsProps {
  stats: GraphStatsType;
  systemStats: SystemStats;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const GraphStats: React.FC<GraphStatsProps> = ({ stats, systemStats, nodes, edges }) => {
  // Calculate additional statistics
  const nodeTypeDistribution = nodes.reduce((acc, node) => {
    acc[node.type] = (acc[node.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const edgeTypeDistribution = edges.reduce((acc, edge) => {
    acc[edge.type] = (acc[edge.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Find most connected nodes
  const nodeConnections = nodes.map(node => {
    const incoming = edges.filter(edge => edge.target === node.id).length;
    const outgoing = edges.filter(edge => edge.source === node.id).length;
    return {
      ...node,
      totalConnections: incoming + outgoing,
      incoming,
      outgoing
    };
  }).sort((a, b) => b.totalConnections - a.totalConnections);

  const topConnectedNodes = nodeConnections.slice(0, 5);

  // Calculate average connections per node
  const avgConnections = nodes.length > 0 
    ? (edges.length * 2) / nodes.length 
    : 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
        Graph Statistics
      </h3>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 14l4-4 4 4"/>
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Nodes</p>
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.total_nodes}</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Total Edges</p>
              <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.total_edges}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-600 dark:text-green-400">Avg Connections</p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">{avgConnections.toFixed(1)}</p>
            </div>
          </div>
        </div>

        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Last Updated</p>
                              <p className="text-sm font-bold text-orange-900 dark:text-orange-100">
                  {new Date(systemStats.last_updated).toLocaleDateString()}
                </p>
            </div>
          </div>
        </div>
      </div>

      {/* Node Type Distribution */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Node Type Distribution
        </h4>
        <div className="space-y-2">
          {Object.entries(nodeTypeDistribution)
            .sort(([,a], [,b]) => b - a)
            .map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getNodeTypeColor(type) }}
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">{type}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        backgroundColor: getNodeTypeColor(type),
                        width: `${(count / stats.total_nodes) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white w-8 text-right">
                    {count}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Edge Type Distribution */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Edge Type Distribution
        </h4>
        <div className="space-y-2">
          {Object.entries(edgeTypeDistribution)
            .sort(([,a], [,b]) => b - a)
            .map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">{type}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-gray-600 dark:bg-gray-400"
                      style={{
                        width: `${(count / stats.total_edges) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white w-8 text-right">
                    {count}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Most Connected Nodes */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Most Connected Nodes
        </h4>
        <div className="space-y-2">
          {topConnectedNodes.map((node, index) => (
            <div key={node.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-md">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400 w-4">
                  #{index + 1}
                </span>
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getNodeTypeColor(node.type) }}
                />
                <span className="text-sm text-gray-900 dark:text-white font-medium">
                  {node.label}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({node.type})
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {node.incoming} in
                </span>
                <span className="text-xs text-gray-400">•</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {node.outgoing} out
                </span>
                <span className="text-xs font-medium text-gray-900 dark:text-white ml-2">
                  {node.totalConnections}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Domain Distribution */}
      {stats.domains && Object.keys(stats.domains).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Domain Distribution
          </h4>
          <div className="space-y-2">
            {Object.entries(stats.domains)
              .sort(([,a], [,b]) => b - a)
              .map(([domain, count]) => (
                <div key={domain} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                    {domain}
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
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
    'default': '#6B7280'
  };
  return colors[type] || colors.default;
};

export default GraphStats; 