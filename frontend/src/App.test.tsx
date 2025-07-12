import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Graph RAG System header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Graph RAG System/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  const queryTabs = screen.getAllByText(/Query Interface/i);
  const graphTabs = screen.getAllByText(/Knowledge Graph/i);
  const documentsTabs = screen.getAllByText(/Document Manager/i);
  
  expect(queryTabs.length).toBeGreaterThan(0);
  expect(graphTabs.length).toBeGreaterThan(0);
  expect(documentsTabs.length).toBeGreaterThan(0);
});

test('renders placeholder content', () => {
  render(<App />);
  const placeholderElement = screen.getByText(/coming soon/i);
  expect(placeholderElement).toBeInTheDocument();
});
