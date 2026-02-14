/**
 * routes.tsx - Lazy-loaded Route Components
 * Improves initial load time by code-splitting pages
 */

import { lazy } from 'react';

// Lazy load page components for code splitting
export const Dashboard = lazy(() => import('./pages/Dashboard'));
export const MCQBrowser = lazy(() => import('./pages/MCQBrowser'));
export const MCQAttempt = lazy(() => import('./pages/MCQAttempt'));
export const PerformanceDashboard = lazy(() => import('./pages/PerformanceDashboard'));

// Auth pages are loaded eagerly (small files, needed immediately)
export { default as Login } from './pages/Login';
export { default as Register } from './pages/Register';
