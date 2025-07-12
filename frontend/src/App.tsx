import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/documents/DocumentUpload';
import DocumentList from './components/documents/DocumentList';
import QueryInterface from './components/query/QueryInterface';
import KnowledgeGraph from './components/graph/KnowledgeGraph';

function App() {
  const [activeTab, setActiveTab] = useState<'query' | 'graph' | 'documents'>('query');
  const [documentView, setDocumentView] = useState<'upload' | 'list'>('upload');

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'query':
        return <QueryInterface />;
      case 'graph':
        return <KnowledgeGraph />;
      case 'documents':
        return (
          <div className="space-y-6">
            {/* Document Manager Header */}
            <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Document Manager
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-2">
                    Upload and manage your documents to build your knowledge graph.
                  </p>
                </div>
                
                {/* Document View Toggle */}
                <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                  <button
                    onClick={() => setDocumentView('upload')}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                      documentView === 'upload'
                        ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    Upload
                  </button>
                  <button
                    onClick={() => setDocumentView('list')}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                      documentView === 'list'
                        ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    Documents
                  </button>
                </div>
              </div>
            </div>

            {/* Document Content */}
            {documentView === 'upload' ? <DocumentUpload /> : <DocumentList />}
          </div>
        );
      default:
        return <QueryInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-primary-50 dark:bg-gray-900">
      {/* Header */}
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

      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            {[
              { id: 'query' as const, label: 'Query Interface', icon: '🔍' },
              { id: 'graph' as const, label: 'Knowledge Graph', icon: '🕸️' },
              { id: 'documents' as const, label: 'Document Manager', icon: '📚' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="animate-fade-in">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
