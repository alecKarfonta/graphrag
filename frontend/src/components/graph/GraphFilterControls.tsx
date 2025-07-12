import React, { useState } from 'react';

interface GraphFilterControlsProps {
  onFiltersChange: (filters: GraphFilters) => void;
  onResetFilters: () => void;
  isLoading?: boolean;
}

export interface GraphFilters {
  domain?: string;
  max_entities: number;
  max_relationships: number;
  min_occurrence: number;
  min_confidence: number;
  entity_types: string[];
  relationship_types: string[];
  sort_by: string;
  sort_order: string;
}

const GraphFilterControls: React.FC<GraphFilterControlsProps> = ({
  onFiltersChange,
  onResetFilters,
  isLoading = false
}) => {
  const [filters, setFilters] = useState<GraphFilters>({
    max_entities: 500,
    max_relationships: 500,
    min_occurrence: 1,
    min_confidence: 0.0,
    entity_types: [],
    relationship_types: [],
    sort_by: 'occurrence',
    sort_order: 'desc'
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleFilterChange = (key: keyof GraphFilters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleEntityTypeToggle = (type: string) => {
    const newTypes = filters.entity_types.includes(type)
      ? filters.entity_types.filter(t => t !== type)
      : [...filters.entity_types, type];
    handleFilterChange('entity_types', newTypes);
  };

  const handleRelationshipTypeToggle = (type: string) => {
    const newTypes = filters.relationship_types.includes(type)
      ? filters.relationship_types.filter(t => t !== type)
      : [...filters.relationship_types, type];
    handleFilterChange('relationship_types', newTypes);
  };

  const handleReset = () => {
    const defaultFilters: GraphFilters = {
      max_entities: 500,
      max_relationships: 500,
      min_occurrence: 1,
      min_confidence: 0.0,
      entity_types: [],
      relationship_types: [],
      sort_by: 'occurrence',
      sort_order: 'desc'
    };
    setFilters(defaultFilters);
    onResetFilters();
  };

  const commonEntityTypes = ['COMPONENT', 'SYSTEM', 'PERSON', 'ORGANIZATION', 'LOCATION', 'TECHNOLOGY'];
  const commonRelationshipTypes = ['part of', 'connected to', 'related to', 'contains', 'works for'];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Graph Filters
        </h3>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-200"
        >
          {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {/* Basic Filters */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Max Entities
          </label>
          <input
            type="number"
            min="1"
            max="5000"
            value={filters.max_entities}
            onChange={(e) => handleFilterChange('max_entities', parseInt(e.target.value) || 500)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Max Relationships
          </label>
          <input
            type="number"
            min="1"
            max="10000"
            value={filters.max_relationships}
            onChange={(e) => handleFilterChange('max_relationships', parseInt(e.target.value) || 500)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Min Occurrence
          </label>
          <input
            type="number"
            min="1"
            value={filters.min_occurrence}
            onChange={(e) => handleFilterChange('min_occurrence', parseInt(e.target.value) || 1)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Min Confidence
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={filters.min_confidence}
            onChange={(e) => handleFilterChange('min_confidence', parseFloat(e.target.value) || 0.0)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="space-y-4 mb-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort By
              </label>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              >
                <option value="occurrence">Occurrence</option>
                <option value="confidence">Confidence</option>
                <option value="name">Name</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort Order
              </label>
              <select
                value={filters.sort_order}
                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>

          {/* Entity Type Filters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Entity Types
            </label>
            <div className="flex flex-wrap gap-2">
              {commonEntityTypes.map(type => (
                <button
                  key={type}
                  onClick={() => handleEntityTypeToggle(type)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                    filters.entity_types.includes(type)
                      ? 'bg-primary-100 dark:bg-primary-900/30 border-primary-500 text-primary-700 dark:text-primary-300'
                      : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  disabled={isLoading}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Relationship Type Filters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Relationship Types
            </label>
            <div className="flex flex-wrap gap-2">
              {commonRelationshipTypes.map(type => (
                <button
                  key={type}
                  onClick={() => handleRelationshipTypeToggle(type)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                    filters.relationship_types.includes(type)
                      ? 'bg-primary-100 dark:bg-primary-900/30 border-primary-500 text-primary-700 dark:text-primary-300'
                      : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  disabled={isLoading}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <button
          onClick={handleReset}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          disabled={isLoading}
        >
          Reset Filters
        </button>

        {isLoading && (
          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Applying filters...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphFilterControls; 