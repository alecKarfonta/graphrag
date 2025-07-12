import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">G</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Graph RAG System
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Intelligent Document Analysis with Knowledge Graphs
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <span className="w-2 h-2 bg-success-500 rounded-full"></span>
              <span>System Online</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}; 