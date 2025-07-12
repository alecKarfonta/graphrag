import React from 'react';
import { GraphNode, GraphEdge } from '../../types/api';

interface GraphControlsProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeType: string | null;
  selectedEdgeType: string | null;
  layout: 'force' | 'circular' | 'hierarchical';
  showLabels: boolean;
  nodeSize: number;
  linkDistance: number;
  onNodeTypeChange: (type: string | null) => void;
  onEdgeTypeChange: (type: string | null) => void;
  onLayoutChange: (layout: 'force' | 'circular' | 'hierarchical') => void;
  onShowLabelsChange: (show: boolean) => void;
  onNodeSizeChange: (size: number) => void;
  onLinkDistanceChange: (distance: number) => void;
  onResetFilters: () => void;
}

const GraphControls: React.FC<GraphControlsProps> = ({
  nodes,
  edges,
  selectedNodeType,
  selectedEdgeType,
  layout,
  showLabels,
  nodeSize,
  linkDistance,
  onNodeTypeChange,
  onEdgeTypeChange,
  onLayoutChange,
  onShowLabelsChange,
  onNodeSizeChange,
  onLinkDistanceChange,
  onResetFilters
}) => {
  // Get unique node types
  const nodeTypes = Array.from(new Set(nodes.map(node => node.type))).sort();
  
  // Get unique edge types
  const edgeTypes = Array.from(new Set(edges.map(edge => edge.type))).sort();

  // Get node type counts
  const nodeTypeCounts = nodeTypes.reduce((acc, type) => {
    acc[type] = nodes.filter(node => node.type === type).length;
    return acc;
  }, {} as Record<string, number>);

  // Get edge type counts
  const edgeTypeCounts = edgeTypes.reduce((acc, type) => {
    acc[type] = edges.filter(edge => edge.type === type).length;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Graph Controls
        </h3>
        <button
          onClick={onResetFilters}
          className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
        >
          Reset All
        </button>
      </div>

      {/* Layout Controls */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Layout
        </h4>
        <div className="grid grid-cols-3 gap-2">
          {(['force', 'circular', 'hierarchical'] as const).map((layoutOption) => (
            <button
              key={layoutOption}
              onClick={() => onLayoutChange(layoutOption)}
              className={`px-3 py-2 text-sm rounded-md transition-colors ${
                layout === layoutOption
                  ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-700'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {layoutOption.charAt(0).toUpperCase() + layoutOption.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Node Type Filter */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Node Types ({nodes.length} total)
        </h4>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          <button
            onClick={() => onNodeTypeChange(null)}
            className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
              selectedNodeType === null
                ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            All Types ({nodes.length})
          </button>
          {nodeTypes.map((type) => (
            <button
              key={type}
              onClick={() => onNodeTypeChange(type)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between ${
                selectedNodeType === type
                  ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{
                    backgroundColor: getNodeTypeColor(type)
                  }}
                />
                <span>{type}</span>
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {nodeTypeCounts[type]}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Edge Type Filter */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Edge Types ({edges.length} total)
        </h4>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          <button
            onClick={() => onEdgeTypeChange(null)}
            className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
              selectedEdgeType === null
                ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            All Types ({edges.length})
          </button>
          {edgeTypes.map((type) => (
            <button
              key={type}
              onClick={() => onEdgeTypeChange(type)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between ${
                selectedEdgeType === type
                  ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span>{type}</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {edgeTypeCounts[type]}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Display Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Display Settings
        </h4>
        <div className="space-y-4">
          {/* Show Labels Toggle */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Show Labels
            </span>
            <button
              onClick={() => onShowLabelsChange(!showLabels)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                showLabels ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  showLabels ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Node Size Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Node Size
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {nodeSize}px
              </span>
            </div>
            <input
              type="range"
              min="4"
              max="20"
              value={nodeSize}
              onChange={(e) => onNodeSizeChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>

          {/* Link Distance Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Link Distance
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {linkDistance}px
              </span>
            </div>
            <input
              type="range"
              min="50"
              max="200"
              value={linkDistance}
              onChange={(e) => onLinkDistanceChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>
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
    'default': '#6B7280'
  };
  return colors[type] || colors.default;
};

export default GraphControls; 