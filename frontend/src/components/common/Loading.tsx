import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'spinner' | 'dots' | 'pulse';
  text?: string;
  className?: string;
}

export const Loading: React.FC<LoadingProps> = ({ 
  size = 'md', 
  variant = 'spinner', 
  text = 'Loading...',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const renderSpinner = () => (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-primary-500 ${sizeClasses[size]}`} />
  );

  const renderDots = () => (
    <div className="flex space-x-1">
      <div className={`bg-primary-500 rounded-full animate-bounce ${sizeClasses[size]}`} style={{ animationDelay: '0ms' }} />
      <div className={`bg-primary-500 rounded-full animate-bounce ${sizeClasses[size]}`} style={{ animationDelay: '150ms' }} />
      <div className={`bg-primary-500 rounded-full animate-bounce ${sizeClasses[size]}`} style={{ animationDelay: '300ms' }} />
    </div>
  );

  const renderPulse = () => (
    <div className={`bg-primary-500 rounded-full animate-pulse ${sizeClasses[size]}`} />
  );

  const renderVariant = () => {
    switch (variant) {
      case 'dots':
        return renderDots();
      case 'pulse':
        return renderPulse();
      default:
        return renderSpinner();
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-4 ${className}`}>
      {renderVariant()}
      {text && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
}; 