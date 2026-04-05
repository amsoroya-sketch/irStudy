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
export const OSCEPractice = lazy(() => import('./pages/OSCEPractice'));
export const OSCESession = lazy(() => import('./pages/OSCESession'));

// EMR pages (lazy loaded)
export const StartEMRSessionPage = lazy(() => import('./pages/emr/StartEMRSessionPage'));
export const EMRSelectSystemPage = lazy(() => import('./pages/emr/EMRSelectSystemPage'));
export const EpicEMRPage = lazy(() => import('./pages/emr/EpicEMRPage'));
export const CernerEMRPage = lazy(() => import('./pages/emr/CernerEMRPage'));

// Mock Exam pages (lazy loaded)
export const MockExamStart = lazy(() => import('./pages/osce/MockExamStart'));
export const MockExamStation = lazy(() => import('./pages/osce/MockExamStation'));
export const MockExamResults = lazy(() => import('./pages/osce/MockExamResults'));

// Auth pages are loaded eagerly (small files, needed immediately)
export { default as Login } from './pages/Login';
export { default as Register } from './pages/Register';
