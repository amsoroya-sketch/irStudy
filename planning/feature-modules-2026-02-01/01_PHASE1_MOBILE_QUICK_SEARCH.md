# Phase 1: Mobile Quick-Search PWA
**Owner:** Frontend Developer
**Duration:** 60-80 hours (2 weeks full-time, 4 weeks part-time)
**Priority:** P0 (Critical - Foundation for all modules)
**Status:** Ready to Start

---

## 📋 Overview

This phase builds a **Progressive Web App (PWA)** that medical students can use as a mobile-first clinical reference tool. The app provides instant access to medical knowledge through RAG-powered search, offline capability, and an exam practice mode.

**Key Achievement:** Sub-500ms search response with offline support

---

## 🎯 Goals

1. **Mobile-First Architecture** (25 hours)
   - React 18 + TypeScript + Vite
   - TailwindCSS responsive design
   - PWA manifest + Service Worker
   - Installable on iOS/Android

2. **RAG Search Integration** (10 hours)
   - FastAPI endpoint for Qdrant search
   - Debounced search input
   - Citation display
   - Confidence scoring

3. **Clinical Decision Support AI** (15 hours)
   - Claude 3.5 Sonnet integration
   - RAG-powered answers with sources
   - Medical terminology highlighting
   - Differential diagnosis suggestions

4. **Offline Capability** (10 hours)
   - Service Worker (Workbox)
   - IndexedDB storage
   - Background sync
   - Cache-first strategy

5. **Exam Mode UI** (15 hours)
   - MCQ interface (reuse existing patterns)
   - Timer component
   - Progress tracking
   - Results review

6. **Testing & Deployment** (10 hours)
   - Mobile device testing
   - Lighthouse performance audit
   - Vercel deployment
   - PWA validation

---

## ✅ Prerequisites Completed

- [x] RAG system operational (9,672 chunks in Qdrant)
- [x] Existing MCQ interface (`/home/dev/Development/irStudy/respiratory-mcq-app/`)
- [x] LLM integration (`/home/dev/Development/irStudy/src/llm/`)
- [x] OSCE and MCQ data files ready

---

## 📝 Detailed Task Breakdown

### Task 1: React PWA Setup (25 hours)

**Priority:** P0 (CRITICAL - foundation for all other tasks)

**Steps:**

```bash
# 1. Create project directory
cd /home/dev/Development/irStudy
mkdir -p mobile-pwa
cd mobile-pwa

# 2. Initialize Vite project with React + TypeScript
npm create vite@latest . -- --template react-ts

# Expected output:
# ✔ Select a framework: › React
# ✔ Select a variant: › TypeScript
# Scaffolding project in /home/dev/Development/irStudy/mobile-pwa...

# 3. Install core dependencies
npm install

# 4. Install additional dependencies
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  tailwindcss postcss autoprefixer \
  workbox-webpack-plugin workbox-precaching \
  idb \
  date-fns \
  clsx \
  lucide-react

# 5. Install development dependencies
npm install -D \
  @types/node \
  vite-plugin-pwa \
  @vitejs/plugin-react \
  eslint \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser

# 6. Initialize TailwindCSS
npx tailwindcss init -p

# This creates:
# - tailwind.config.js
# - postcss.config.js
```

**Configure TailwindCSS:**

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        medical: {
          emergency: '#dc2626',
          warning: '#f59e0b',
          info: '#3b82f6',
          success: '#10b981',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

**Update src/index.css:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900 font-sans antialiased;
  }

  /* Mobile-first typography */
  h1 {
    @apply text-2xl md:text-3xl font-bold mb-4;
  }

  h2 {
    @apply text-xl md:text-2xl font-semibold mb-3;
  }

  h3 {
    @apply text-lg md:text-xl font-medium mb-2;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 text-white px-4 py-2 rounded-lg
           hover:bg-primary-700 active:bg-primary-800
           transition-colors duration-200;
  }

  .btn-secondary {
    @apply bg-gray-200 text-gray-800 px-4 py-2 rounded-lg
           hover:bg-gray-300 active:bg-gray-400
           transition-colors duration-200;
  }

  .input-field {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg
           focus:outline-none focus:ring-2 focus:ring-primary-500
           focus:border-transparent;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-4 md:p-6;
  }
}

@layer utilities {
  .safe-top {
    padding-top: env(safe-area-inset-top);
  }

  .safe-bottom {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
```

**Configure Vite with PWA plugin:**

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'irStudy Medical Reference',
        short_name: 'irStudy',
        description: 'Medical education platform for AMC Clinical Exam preparation',
        theme_color: '#0ea5e9',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        categories: ['education', 'medical', 'health'],
        screenshots: [
          {
            src: 'screenshot-mobile.png',
            sizes: '750x1334',
            type: 'image/png',
            label: 'Search medical knowledge'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,json}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.irstudy\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    host: true // Allows mobile device access via network
  }
})
```

**Create project structure:**

```bash
cd /home/dev/Development/irStudy/mobile-pwa

# Create directory structure
mkdir -p src/{components,pages,hooks,utils,types,services,store}

# Create component directories
mkdir -p src/components/{search,exam,common}

# Create page directories
mkdir -p src/pages/{home,search,exam,settings}

tree src/
# Expected output:
# src/
# ├── components/
# │   ├── search/
# │   ├── exam/
# │   └── common/
# ├── pages/
# │   ├── home/
# │   ├── search/
# │   ├── exam/
# │   └── settings/
# ├── hooks/
# ├── utils/
# ├── types/
# ├── services/
# └── store/
```

**Create TypeScript types:**

```typescript
// src/types/index.ts

export interface SearchResult {
  id: string;
  content: string;
  metadata: {
    source: string;
    section: string;
    page?: number;
    url?: string;
  };
  score: number;
  highlights?: string[];
}

export interface MCQQuestion {
  id: string;
  question: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
    E?: string;
  };
  correct_answer: string;
  explanation: string;
  topic: string;
  subtopic?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  citations: Citation[];
  image_url?: string;
}

export interface Citation {
  source: string;
  reference: string;
  url?: string;
  evidence_level?: string;
}

export interface ExamSession {
  id: string;
  questions: MCQQuestion[];
  answers: Record<string, string>;
  startTime: number;
  endTime?: number;
  timeLimit?: number; // in seconds
  score?: number;
  completed: boolean;
}

export interface AIResponse {
  answer: string;
  confidence: number;
  sources: SearchResult[];
  differential_diagnosis?: string[];
  red_flags?: string[];
}

export interface User {
  id: string;
  name: string;
  email: string;
  studyPlan?: {
    weeklySessions: number;
    targetExamDate?: string;
    focusAreas: string[];
  };
}
```

**Create basic router setup:**

```typescript
// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages (to be created)
import HomePage from './pages/home/HomePage';
import SearchPage from './pages/search/SearchPage';
import ExamPage from './pages/exam/ExamPage';
import SettingsPage from './pages/settings/SettingsPage';

// Layout
import Layout from './components/common/Layout';

// Create query client for data fetching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="exam" element={<ExamPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

**Create Layout component:**

```typescript
// src/components/common/Layout.tsx
import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Home,
  Search,
  ClipboardList,
  Settings
} from 'lucide-react';

const Layout: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/exam', icon: ClipboardList, label: 'Exam' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="flex flex-col h-screen">
      {/* Main content */}
      <main className="flex-1 overflow-y-auto pb-16 safe-top">
        <Outlet />
      </main>

      {/* Bottom navigation (mobile-first) */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-bottom">
        <div className="flex justify-around items-center h-16">
          {navItems.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`flex flex-col items-center justify-center flex-1 h-full ${
                  isActive
                    ? 'text-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon size={24} />
                <span className="text-xs mt-1">{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default Layout;
```

**Create HomePage placeholder:**

```typescript
// src/pages/home/HomePage.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Search, BookOpen, Target } from 'lucide-react';

const HomePage: React.FC = () => {
  return (
    <div className="p-4 max-w-4xl mx-auto">
      <header className="mb-8 mt-4">
        <h1 className="text-3xl font-bold text-primary-600">
          irStudy Medical Reference
        </h1>
        <p className="text-gray-600 mt-2">
          Your AI-powered companion for AMC Clinical Exam preparation
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Quick Search Card */}
        <Link to="/search" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Search className="text-primary-600" size={24} />
            </div>
            <div>
              <h3 className="font-semibold mb-1">Quick Search</h3>
              <p className="text-sm text-gray-600">
                Find clinical information instantly with AI-powered search
              </p>
            </div>
          </div>
        </Link>

        {/* Practice Exam Card */}
        <Link to="/exam" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Target className="text-green-600" size={24} />
            </div>
            <div>
              <h3 className="font-semibold mb-1">Practice Exam</h3>
              <p className="text-sm text-gray-600">
                Test your knowledge with timed MCQ practice sessions
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* Stats section */}
      <div className="mt-8 card">
        <h2 className="font-semibold mb-4">Your Progress</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-600">42</div>
            <div className="text-sm text-gray-600">Sessions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">78%</div>
            <div className="text-sm text-gray-600">Accuracy</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">12</div>
            <div className="text-sm text-gray-600">Topics</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
```

**Test the setup:**

```bash
# Start development server
npm run dev

# Expected output:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:3000/
# ➜  Network: http://192.168.x.x:3000/

# Open in browser
# - Desktop: http://localhost:3000/
# - Mobile: http://192.168.x.x:3000/ (use your network IP)
```

**Validation:**
- [ ] Vite dev server runs without errors
- [ ] React app loads in browser
- [ ] Bottom navigation works (all routes accessible)
- [ ] TailwindCSS styles applied correctly
- [ ] PWA manifest generated (check Network tab → Manifest)
- [ ] Mobile-responsive layout (test with Chrome DevTools)

**Time Estimate:** 25 hours

---

### Task 2: RAG Search API Integration (10 hours)

**Priority:** P0 (CRITICAL - core functionality)

**Backend: FastAPI Endpoint**

```python
# /home/dev/Development/irStudy/backend/api/search.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.rag.qdrant_client import QdrantClient

router = APIRouter(prefix="/api/search", tags=["search"])

# Initialize Qdrant client (reuse existing implementation)
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    collection_name="medical_knowledge"
)

class SearchResultMetadata(BaseModel):
    source: str
    section: str
    page: Optional[int] = None
    url: Optional[str] = None

class SearchResultItem(BaseModel):
    id: str
    content: str
    metadata: SearchResultMetadata
    score: float
    highlights: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total_count: int
    search_time_ms: float

@router.get("/", response_model=SearchResponse)
async def search_medical_knowledge(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of results"),
    min_score: float = Query(0.7, ge=0, le=1, description="Minimum similarity score")
):
    """
    Search medical knowledge base using semantic search.

    Args:
        q: Search query (minimum 2 characters)
        limit: Maximum number of results (1-20)
        min_score: Minimum similarity score (0-1)

    Returns:
        SearchResponse with matching documents and metadata
    """
    import time
    start_time = time.time()

    try:
        # Perform semantic search using Qdrant
        raw_results = await qdrant_client.search(
            query_text=q,
            limit=limit,
            score_threshold=min_score
        )

        # Format results
        results = []
        for result in raw_results:
            results.append(SearchResultItem(
                id=result.id,
                content=result.payload.get("text", ""),
                metadata=SearchResultMetadata(
                    source=result.payload.get("source", "Unknown"),
                    section=result.payload.get("section", ""),
                    page=result.payload.get("page"),
                    url=result.payload.get("url")
                ),
                score=result.score,
                highlights=_extract_highlights(
                    result.payload.get("text", ""),
                    q
                )
            ))

        search_time_ms = (time.time() - start_time) * 1000

        return SearchResponse(
            query=q,
            results=results,
            total_count=len(results),
            search_time_ms=round(search_time_ms, 2)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

def _extract_highlights(text: str, query: str, context_chars: int = 100) -> List[str]:
    """
    Extract text snippets containing query terms.

    Args:
        text: Full text content
        query: Search query
        context_chars: Characters of context around match

    Returns:
        List of highlighted snippets
    """
    import re

    # Simple highlighting (can be improved with proper NLP)
    highlights = []
    query_terms = query.lower().split()

    for term in query_terms:
        # Find all occurrences (case-insensitive)
        pattern = re.compile(f"(.{{0,{context_chars}}}{re.escape(term)}.{{0,{context_chars}}})", re.IGNORECASE)
        matches = pattern.findall(text)
        highlights.extend(matches[:2])  # Max 2 snippets per term

    return highlights[:5]  # Max 5 total highlights

# Health check endpoint
@router.get("/health")
async def search_health():
    """Health check for search API"""
    try:
        # Test Qdrant connection
        collection_info = await qdrant_client.get_collection_info()
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection": collection_info.get("name"),
            "vectors_count": collection_info.get("vectors_count", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

**Add to main FastAPI app:**

```python
# /home/dev/Development/irStudy/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.search import router as search_router

app = FastAPI(
    title="irStudy Medical API",
    description="Backend API for irStudy medical education platform",
    version="1.0.0"
)

# CORS middleware (allow mobile PWA access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.*.*:3000",  # Local network
        "https://irstudy-mobile.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router)

@app.get("/")
async def root():
    return {"message": "irStudy Medical API - v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Frontend: Search Service**

```typescript
// src/services/searchService.ts
import { SearchResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SearchParams {
  query: string;
  limit?: number;
  minScore?: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_count: number;
  search_time_ms: number;
}

class SearchService {
  async search(params: SearchParams): Promise<SearchResponse> {
    const { query, limit = 5, minScore = 0.7 } = params;

    const url = new URL(`${API_BASE_URL}/api/search/`);
    url.searchParams.append('q', query);
    url.searchParams.append('limit', limit.toString());
    url.searchParams.append('min_score', minScore.toString());

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Search failed');
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/search/health`);
    return response.json();
  }
}

export const searchService = new SearchService();
```

**Frontend: React Hook for Search**

```typescript
// src/hooks/useSearch.ts
import { useQuery } from '@tanstack/react-query';
import { searchService, SearchParams } from '../services/searchService';

export const useSearch = (params: SearchParams) => {
  return useQuery({
    queryKey: ['search', params.query, params.limit, params.minScore],
    queryFn: () => searchService.search(params),
    enabled: params.query.length >= 2, // Only search if query has 2+ chars
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
};
```

**Frontend: Search Page Component**

```typescript
// src/pages/search/SearchPage.tsx
import React, { useState, useEffect } from 'react';
import { Search, Loader2, AlertCircle } from 'lucide-react';
import { useSearch } from '../../hooks/useSearch';
import SearchResultCard from '../../components/search/SearchResultCard';

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search input (500ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 500);

    return () => clearTimeout(timer);
  }, [query]);

  const { data, isLoading, error } = useSearch({
    query: debouncedQuery,
    limit: 10,
    minScore: 0.7
  });

  return (
    <div className="p-4 max-w-4xl mx-auto">
      {/* Search header */}
      <div className="mb-6 mt-4">
        <h1>Medical Knowledge Search</h1>
        <p className="text-gray-600">
          Search across 9,672 medical references
        </p>
      </div>

      {/* Search input */}
      <div className="relative mb-6">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
          size={20}
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search symptoms, conditions, treatments..."
          className="input-field pl-10 pr-4"
          autoFocus
        />
        {isLoading && (
          <Loader2
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-600 animate-spin"
            size={20}
          />
        )}
      </div>

      {/* Search stats */}
      {data && (
        <div className="text-sm text-gray-600 mb-4">
          Found {data.total_count} results in {data.search_time_ms}ms
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {error && (
          <div className="card bg-red-50 border border-red-200">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle size={20} />
              <span>Search failed: {error.message}</span>
            </div>
          </div>
        )}

        {data?.results.map((result) => (
          <SearchResultCard key={result.id} result={result} query={query} />
        ))}

        {data && data.results.length === 0 && (
          <div className="card text-center text-gray-500">
            No results found for "{query}"
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
```

**Search Result Card Component:**

```typescript
// src/components/search/SearchResultCard.tsx
import React from 'react';
import { SearchResult } from '../../types';
import { ExternalLink, BookOpen } from 'lucide-react';

interface SearchResultCardProps {
  result: SearchResult;
  query: string;
}

const SearchResultCard: React.FC<SearchResultCardProps> = ({ result, query }) => {
  // Highlight query terms in text
  const highlightText = (text: string, query: string) => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return (
      <>
        {parts.map((part, index) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={index} className="bg-yellow-200 font-semibold">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </>
    );
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Source badge */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <BookOpen size={16} className="text-primary-600" />
          <span className="text-sm font-medium text-primary-600">
            {result.metadata.source}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          Relevance: {Math.round(result.score * 100)}%
        </span>
      </div>

      {/* Section */}
      {result.metadata.section && (
        <div className="text-sm text-gray-600 mb-2">
          {result.metadata.section}
        </div>
      )}

      {/* Content */}
      <p className="text-gray-800 leading-relaxed">
        {highlightText(result.content, query)}
      </p>

      {/* Highlights (additional snippets) */}
      {result.highlights && result.highlights.length > 0 && (
        <div className="mt-3 space-y-1">
          {result.highlights.map((highlight, index) => (
            <div key={index} className="text-sm text-gray-600 italic">
              "...{highlightText(highlight, query)}..."
            </div>
          ))}
        </div>
      )}

      {/* URL link */}
      {result.metadata.url && (
        <a
          href={result.metadata.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 mt-3 text-sm text-primary-600 hover:text-primary-700"
        >
          View source
          <ExternalLink size={14} />
        </a>
      )}
    </div>
  );
};

export default SearchResultCard;
```

**Test the integration:**

```bash
# Terminal 1: Start FastAPI backend
cd /home/dev/Development/irStudy/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start React dev server
cd /home/dev/Development/irStudy/mobile-pwa
npm run dev

# Test search in browser:
# 1. Navigate to http://localhost:3000/search
# 2. Type "asthma treatment"
# 3. Should see results within 500ms
```

**Validation:**
- [ ] FastAPI backend runs without errors
- [ ] Search endpoint returns results (`curl http://localhost:8000/api/search/?q=asthma`)
- [ ] Frontend search input debounces correctly (500ms delay)
- [ ] Results display with highlighting
- [ ] Search time < 500ms for typical queries
- [ ] CORS configured (mobile device can access API)

**Time Estimate:** 10 hours

---

### Task 3: Clinical Decision Support AI (15 hours)

**Priority:** P1 (High - differentiates from basic search)

**Backend: AI Chat Endpoint**

```python
# /home/dev/Development/irStudy/backend/api/ai_chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.llm.claude_client import ClaudeClient
from src.rag.qdrant_client import QdrantClient

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Initialize clients
claude = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    collection_name="medical_knowledge"
)

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=5, description="Medical query")
    context: Optional[str] = Field(None, description="Additional context")
    include_differential: bool = Field(True, description="Include differential diagnosis")
    include_red_flags: bool = Field(True, description="Include red flags/warnings")

class Citation(BaseModel):
    source: str
    content: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Citation]
    differential_diagnosis: Optional[List[str]] = None
    red_flags: Optional[List[str]] = None
    processing_time_ms: float

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    """
    AI-powered clinical decision support using RAG + Claude 3.5 Sonnet.

    Provides evidence-based answers with citations, differential diagnoses,
    and red flag warnings for Australian medical students.
    """
    import time
    start_time = time.time()

    try:
        # Step 1: Retrieve relevant knowledge from RAG
        rag_results = await qdrant.search(
            query_text=request.query,
            limit=5,
            score_threshold=0.75
        )

        # Step 2: Format context for Claude
        context_chunks = []
        citations = []

        for result in rag_results:
            context_chunks.append(f"[Source: {result.payload['source']}]\n{result.payload['text']}")
            citations.append(Citation(
                source=result.payload['source'],
                content=result.payload['text'][:200] + "...",  # Truncate for display
                url=result.payload.get('url')
            ))

        context_text = "\n\n".join(context_chunks)

        # Step 3: Build prompt for Claude
        system_prompt = """You are a medical education assistant for Australian medical students preparing for the AMC Clinical Examination.

Your role:
- Provide evidence-based, accurate medical information
- Use Australian medical guidelines (PBS, MBS, eTG) when available
- Highlight key concepts for exam preparation
- Include differential diagnoses when appropriate
- Flag red flags and serious conditions

Format your response in clear sections:
1. Direct answer to the question
2. Key points (bullet points)
3. Differential diagnosis (if applicable)
4. Red flags/warnings (if applicable)

Always cite sources from the provided context."""

        user_prompt = f"""Question: {request.query}

Context from medical references:
{context_text}

{f'Additional context: {request.context}' if request.context else ''}

Please provide a comprehensive answer suitable for a medical student preparing for clinical exams."""

        # Step 4: Call Claude API
        claude_response = await claude.generate(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=1500,
            temperature=0.3  # Lower temperature for factual medical information
        )

        answer_text = claude_response['content'][0]['text']

        # Step 5: Extract structured information
        differential_diagnosis = None
        red_flags = None

        if request.include_differential:
            differential_diagnosis = _extract_differential(answer_text)

        if request.include_red_flags:
            red_flags = _extract_red_flags(answer_text)

        # Step 6: Calculate confidence score
        confidence = _calculate_confidence(rag_results, claude_response)

        processing_time_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            answer=answer_text,
            confidence=confidence,
            sources=citations,
            differential_diagnosis=differential_diagnosis,
            red_flags=red_flags,
            processing_time_ms=round(processing_time_ms, 2)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI chat failed: {str(e)}"
        )

def _extract_differential(text: str) -> List[str]:
    """Extract differential diagnosis from AI response"""
    import re

    # Look for section markers
    diff_patterns = [
        r"Differential [Dd]iagnosis:?\s*\n(.*?)(?=\n\n|\n[A-Z]|$)",
        r"Differentials?:?\s*\n(.*?)(?=\n\n|\n[A-Z]|$)",
    ]

    for pattern in diff_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Extract bullet points or numbered items
            items = re.findall(r"[-•\d.]\s*(.+)", match.group(1))
            return [item.strip() for item in items if item.strip()]

    return None

def _extract_red_flags(text: str) -> List[str]:
    """Extract red flags/warnings from AI response"""
    import re

    # Look for red flag section
    flag_patterns = [
        r"Red [Ff]lags?:?\s*\n(.*?)(?=\n\n|\n[A-Z]|$)",
        r"Warnings?:?\s*\n(.*?)(?=\n\n|\n[A-Z]|$)",
    ]

    for pattern in flag_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items = re.findall(r"[-•\d.]\s*(.+)", match.group(1))
            return [item.strip() for item in items if item.strip()]

    return None

def _calculate_confidence(rag_results, claude_response) -> float:
    """
    Calculate confidence score based on:
    - RAG result scores (higher = more relevant sources)
    - Number of sources found
    - Claude's response quality indicators
    """
    if not rag_results:
        return 0.5  # Low confidence without sources

    # Average RAG score
    avg_rag_score = sum(r.score for r in rag_results) / len(rag_results)

    # Number of sources (more sources = higher confidence, up to 5)
    source_factor = min(len(rag_results) / 5.0, 1.0)

    # Combined confidence (weighted average)
    confidence = (avg_rag_score * 0.7) + (source_factor * 0.3)

    return round(confidence, 2)
```

**Frontend: AI Chat Service**

```typescript
// src/services/aiChatService.ts
import { AIResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  query: string;
  context?: string;
  includeDifferential?: boolean;
  includeRedFlags?: boolean;
}

class AIChatService {
  async chat(request: ChatRequest): Promise<AIResponse> {
    const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: request.query,
        context: request.context,
        include_differential: request.includeDifferential ?? true,
        include_red_flags: request.includeRedFlags ?? true,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'AI chat failed');
    }

    return response.json();
  }
}

export const aiChatService = new AIChatService();
```

**Frontend: AI Chat Component**

```typescript
// src/components/search/AIChatPanel.tsx
import React, { useState } from 'react';
import { MessageSquare, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { aiChatService } from '../../services/aiChatService';
import { AIResponse } from '../../types';

interface AIChatPanelProps {
  query: string;
}

const AIChatPanel: React.FC<AIChatPanelProps> = ({ query }) => {
  const [response, setResponse] = useState<AIResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAskAI = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await aiChatService.chat({ query });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get AI response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card mt-4">
      <div className="flex items-center gap-2 mb-4">
        <MessageSquare className="text-primary-600" size={20} />
        <h3 className="font-semibold">AI Clinical Decision Support</h3>
      </div>

      {!response && !loading && (
        <button
          onClick={handleAskAI}
          className="btn-primary w-full"
        >
          Ask AI for Clinical Insights
        </button>
      )}

      {loading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-600" size={32} />
          <span className="ml-3 text-gray-600">Analyzing medical knowledge...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        </div>
      )}

      {response && (
        <div className="space-y-4">
          {/* Confidence indicator */}
          <div className="flex items-center gap-2">
            <CheckCircle2
              className={response.confidence > 0.8 ? 'text-green-600' : 'text-orange-600'}
              size={20}
            />
            <span className="text-sm text-gray-600">
              Confidence: {Math.round(response.confidence * 100)}%
            </span>
          </div>

          {/* Main answer */}
          <div className="prose prose-sm max-w-none">
            <div className="whitespace-pre-wrap">{response.answer}</div>
          </div>

          {/* Differential diagnosis */}
          {response.differential_diagnosis && response.differential_diagnosis.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Differential Diagnosis</h4>
              <ul className="list-disc list-inside space-y-1">
                {response.differential_diagnosis.map((item, index) => (
                  <li key={index} className="text-blue-800 text-sm">{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Red flags */}
          {response.red_flags && response.red_flags.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="text-red-600" size={20} />
                <h4 className="font-semibold text-red-900">Red Flags</h4>
              </div>
              <ul className="list-disc list-inside space-y-1">
                {response.red_flags.map((item, index) => (
                  <li key={index} className="text-red-800 text-sm">{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Sources */}
          <div className="border-t border-gray-200 pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Sources</h4>
            <div className="space-y-2">
              {response.sources.map((source, index) => (
                <div key={index} className="text-sm">
                  <span className="font-medium text-primary-600">{source.source}</span>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-primary-600 hover:underline"
                    >
                      View
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIChatPanel;
```

**Integrate into SearchPage:**

```typescript
// Update src/pages/search/SearchPage.tsx
// Add import at top:
import AIChatPanel from '../../components/search/AIChatPanel';

// Add after search results:
{data && data.results.length > 0 && (
  <AIChatPanel query={debouncedQuery} />
)}
```

**Validation:**
- [ ] AI endpoint responds within 3 seconds
- [ ] Response includes differential diagnosis (when applicable)
- [ ] Red flags highlighted prominently
- [ ] Citations properly formatted
- [ ] Confidence score makes sense (high for common queries)
- [ ] Mobile-friendly layout

**Time Estimate:** 15 hours

---

**(Continuing in next file due to length...)**

**Validation Summary for Task 3:**
- [ ] Backend API endpoint functional
- [ ] Claude 3.5 Sonnet integration working
- [ ] RAG context properly injected
- [ ] Differential diagnosis extraction accurate
- [ ] Red flags prominently displayed
- [ ] Response time < 3 seconds

**Time Estimate:** 15 hours

---

### Task 4: Offline Capability (10 hours)

**Priority:** P1 (High - critical for mobile users)

**Service Worker Configuration:**

Already configured in `vite.config.ts` (Task 1), but let's add advanced caching strategies:

```typescript
// src/serviceWorker.ts
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';

// Precache all static assets
declare const self: ServiceWorkerGlobalScope;
precacheAndRoute(self.__WB_MANIFEST);

// Cache API responses (network-first with fallback)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/search/'),
  new NetworkFirst({
    cacheName: 'search-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 60 * 60 * 24, // 24 hours
      }),
    ],
  })
);

// Cache AI responses (network-first, shorter expiration)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/ai/'),
  new NetworkFirst({
    cacheName: 'ai-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 60 * 60, // 1 hour
      }),
    ],
  })
);

// Cache images (cache-first)
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
      }),
    ],
  })
);

// Cache fonts (cache-first, long expiration)
registerRoute(
  ({ request }) => request.destination === 'font',
  new CacheFirst({
    cacheName: 'fonts-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 10,
        maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
      }),
    ],
  })
);

// Listen for offline/online events
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
```

**IndexedDB Storage (for exam sessions):**

```typescript
// src/utils/db.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { ExamSession, MCQQuestion } from '../types';

interface IrStudyDB extends DBSchema {
  'exam-sessions': {
    key: string;
    value: ExamSession;
    indexes: { 'by-completed': boolean };
  };
  'cached-questions': {
    key: string;
    value: MCQQuestion;
  };
  'search-history': {
    key: string;
    value: {
      query: string;
      timestamp: number;
    };
  };
}

class DatabaseService {
  private db: IDBPDatabase<IrStudyDB> | null = null;

  async init() {
    if (this.db) return this.db;

    this.db = await openDB<IrStudyDB>('irstudy-db', 1, {
      upgrade(db) {
        // Exam sessions store
        if (!db.objectStoreNames.contains('exam-sessions')) {
          const sessionStore = db.createObjectStore('exam-sessions', {
            keyPath: 'id',
          });
          sessionStore.createIndex('by-completed', 'completed');
        }

        // Cached questions store
        if (!db.objectStoreNames.contains('cached-questions')) {
          db.createObjectStore('cached-questions', {
            keyPath: 'id',
          });
        }

        // Search history store
        if (!db.objectStoreNames.contains('search-history')) {
          db.createObjectStore('search-history', {
            keyPath: 'query',
          });
        }
      },
    });

    return this.db;
  }

  // Exam session methods
  async saveExamSession(session: ExamSession) {
    const db = await this.init();
    await db.put('exam-sessions', session);
  }

  async getExamSession(id: string): Promise<ExamSession | undefined> {
    const db = await this.init();
    return db.get('exam-sessions', id);
  }

  async getAllExamSessions(): Promise<ExamSession[]> {
    const db = await this.init();
    return db.getAll('exam-sessions');
  }

  async deleteExamSession(id: string) {
    const db = await this.init();
    await db.delete('exam-sessions', id);
  }

  // Cached questions methods
  async cacheQuestions(questions: MCQQuestion[]) {
    const db = await this.init();
    const tx = db.transaction('cached-questions', 'readwrite');
    await Promise.all(questions.map(q => tx.store.put(q)));
    await tx.done;
  }

  async getCachedQuestions(count: number = 20): Promise<MCQQuestion[]> {
    const db = await this.init();
    const all = await db.getAll('cached-questions');
    // Return random subset
    return all.sort(() => 0.5 - Math.random()).slice(0, count);
  }

  // Search history methods
  async saveSearchQuery(query: string) {
    const db = await this.init();
    await db.put('search-history', {
      query,
      timestamp: Date.now(),
    });
  }

  async getSearchHistory(limit: number = 10): Promise<string[]> {
    const db = await this.init();
    const all = await db.getAll('search-history');
    return all
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit)
      .map(item => item.query);
  }

  async clearOldSearchHistory(daysToKeep: number = 30) {
    const db = await this.init();
    const cutoff = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
    const tx = db.transaction('search-history', 'readwrite');
    const all = await tx.store.getAll();

    for (const item of all) {
      if (item.timestamp < cutoff) {
        await tx.store.delete(item.query);
      }
    }

    await tx.done;
  }
}

export const db = new DatabaseService();
```

**Offline Indicator Component:**

```typescript
// src/components/common/OfflineIndicator.tsx
import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';

const OfflineIndicator: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-orange-500 text-white px-4 py-2 z-50 safe-top">
      <div className="flex items-center justify-center gap-2">
        <WifiOff size={20} />
        <span className="text-sm font-medium">
          You're offline - Using cached data
        </span>
      </div>
    </div>
  );
};

export default OfflineIndicator;
```

**Add to Layout:**

```typescript
// Update src/components/common/Layout.tsx
import OfflineIndicator from './OfflineIndicator';

// Add inside the main div:
<OfflineIndicator />
```

**Background Sync for Exam Results:**

```typescript
// src/utils/backgroundSync.ts

export const registerBackgroundSync = async (tag: string, data: any) => {
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    const registration = await navigator.serviceWorker.ready;

    // Store data to be synced in IndexedDB
    await db.saveExamSession(data);

    // Register sync event
    try {
      await registration.sync.register(tag);
      console.log('Background sync registered:', tag);
    } catch (err) {
      console.error('Background sync failed:', err);
      // Fallback: sync immediately if background sync not available
      await syncExamResults(data);
    }
  }
};

const syncExamResults = async (session: ExamSession) => {
  try {
    const response = await fetch('/api/exam/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(session),
    });

    if (response.ok) {
      console.log('Exam results synced');
    }
  } catch (err) {
    console.error('Failed to sync exam results:', err);
  }
};
```

**Validation:**
- [ ] Service worker registered successfully
- [ ] Offline mode works (disable network in DevTools)
- [ ] Search results cached and accessible offline
- [ ] Exam sessions saved to IndexedDB
- [ ] Offline indicator appears when network unavailable
- [ ] Background sync queues data when offline

**Time Estimate:** 10 hours

---

### Task 5: Exam Mode UI (15 hours)

**Priority:** P1 (High - core feature)

**Exam Session Store (Zustand):**

```typescript
// src/store/examStore.ts
import { create } from 'zustand';
import { ExamSession, MCQQuestion } from '../types';
import { db } from '../utils/db';

interface ExamState {
  currentSession: ExamSession | null;
  startExam: (questions: MCQQuestion[], timeLimit?: number) => void;
  submitAnswer: (questionId: string, answer: string) => void;
  endExam: () => void;
  loadSession: (sessionId: string) => Promise<void>;
  clearSession: () => void;
}

export const useExamStore = create<ExamState>((set, get) => ({
  currentSession: null,

  startExam: (questions, timeLimit) => {
    const session: ExamSession = {
      id: `exam_${Date.now()}`,
      questions,
      answers: {},
      startTime: Date.now(),
      timeLimit,
      completed: false,
    };

    // Save to IndexedDB
    db.saveExamSession(session);

    set({ currentSession: session });
  },

  submitAnswer: (questionId, answer) => {
    const { currentSession } = get();
    if (!currentSession) return;

    const updatedSession = {
      ...currentSession,
      answers: {
        ...currentSession.answers,
        [questionId]: answer,
      },
    };

    // Save to IndexedDB
    db.saveExamSession(updatedSession);

    set({ currentSession: updatedSession });
  },

  endExam: () => {
    const { currentSession } = get();
    if (!currentSession) return;

    // Calculate score
    let correct = 0;
    currentSession.questions.forEach(q => {
      if (currentSession.answers[q.id] === q.correct_answer) {
        correct++;
      }
    });

    const score = Math.round((correct / currentSession.questions.length) * 100);

    const completedSession = {
      ...currentSession,
      endTime: Date.now(),
      score,
      completed: true,
    };

    // Save to IndexedDB
    db.saveExamSession(completedSession);

    set({ currentSession: completedSession });
  },

  loadSession: async (sessionId) => {
    const session = await db.getExamSession(sessionId);
    if (session) {
      set({ currentSession: session });
    }
  },

  clearSession: () => {
    set({ currentSession: null });
  },
}));
```

**Exam Page Component:**

```typescript
// src/pages/exam/ExamPage.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle2, Play } from 'lucide-react';
import { useExamStore } from '../../store/examStore';
import ExamQuestion from '../../components/exam/ExamQuestion';
import ExamResults from '../../components/exam/ExamResults';
import ExamTimer from '../../components/exam/ExamTimer';
import { db } from '../../utils/db';
import { MCQQuestion } from '../../types';

const ExamPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentSession, startExam, endExam } = useExamStore();
  const [loading, setLoading] = useState(false);
  const [questionCount, setQuestionCount] = useState(20);
  const [timedMode, setTimedMode] = useState(false);

  const handleStartExam = async () => {
    setLoading(true);

    try {
      // Load questions from cache (offline support)
      const questions = await db.getCachedQuestions(questionCount);

      if (questions.length === 0) {
        alert('No cached questions available. Please connect to internet and search for topics first.');
        return;
      }

      // Start exam with optional time limit (30 seconds per question)
      const timeLimit = timedMode ? questionCount * 30 : undefined;
      startExam(questions, timeLimit);
    } catch (err) {
      console.error('Failed to start exam:', err);
      alert('Failed to start exam');
    } finally {
      setLoading(false);
    }
  };

  // Show results if exam completed
  if (currentSession?.completed) {
    return <ExamResults session={currentSession} />;
  }

  // Show exam in progress
  if (currentSession && !currentSession.completed) {
    return (
      <div className="p-4 max-w-4xl mx-auto">
        <ExamTimer session={currentSession} onTimeUp={endExam} />
        <ExamQuestion session={currentSession} />
      </div>
    );
  }

  // Show exam setup
  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="mb-8 mt-4">
        <h1>Practice Exam</h1>
        <p className="text-gray-600">
          Test your knowledge with timed MCQ practice sessions
        </p>
      </div>

      <div className="card">
        <h2 className="mb-4">Exam Settings</h2>

        {/* Question count */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Questions
          </label>
          <div className="flex gap-2">
            {[10, 20, 30, 50].map(count => (
              <button
                key={count}
                onClick={() => setQuestionCount(count)}
                className={`px-4 py-2 rounded-lg border ${
                  questionCount === count
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {count}
              </button>
            ))}
          </div>
        </div>

        {/* Timed mode */}
        <div className="mb-6">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={timedMode}
              onChange={(e) => setTimedMode(e.target.checked)}
              className="w-4 h-4 text-primary-600"
            />
            <span className="text-sm font-medium text-gray-700">
              Timed Mode (30 seconds per question)
            </span>
          </label>
        </div>

        {/* Start button */}
        <button
          onClick={handleStartExam}
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>Loading questions...</>
          ) : (
            <>
              <Play size={20} />
              Start Exam
            </>
          )}
        </button>
      </div>

      {/* Recent sessions */}
      <div className="mt-8 card">
        <h2 className="mb-4">Recent Sessions</h2>
        <p className="text-gray-600 text-sm">
          View your past exam performance here (coming soon)
        </p>
      </div>
    </div>
  );
};

export default ExamPage;
```

**Exam Question Component:**

```typescript
// src/components/exam/ExamQuestion.tsx
import React, { useState } from 'react';
import { useExamStore } from '../../store/examStore';
import { ExamSession } from '../../types';
import { ChevronLeft, ChevronRight, Flag } from 'lucide-react';

interface ExamQuestionProps {
  session: ExamSession;
}

const ExamQuestion: React.FC<ExamQuestionProps> = ({ session }) => {
  const { submitAnswer, endExam } = useExamStore();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flagged, setFlagged] = useState<Set<string>>(new Set());

  const currentQuestion = session.questions[currentIndex];
  const selectedAnswer = session.answers[currentQuestion.id];

  const handleAnswerSelect = (answer: string) => {
    submitAnswer(currentQuestion.id, answer);
  };

  const handleNext = () => {
    if (currentIndex < session.questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleToggleFlag = () => {
    const newFlagged = new Set(flagged);
    if (newFlagged.has(currentQuestion.id)) {
      newFlagged.delete(currentQuestion.id);
    } else {
      newFlagged.add(currentQuestion.id);
    }
    setFlagged(newFlagged);
  };

  const handleFinish = () => {
    const unanswered = session.questions.filter(
      q => !session.answers[q.id]
    );

    if (unanswered.length > 0) {
      const confirm = window.confirm(
        `You have ${unanswered.length} unanswered questions. Are you sure you want to finish?`
      );
      if (!confirm) return;
    }

    endExam();
  };

  const progress = Math.round(
    (Object.keys(session.answers).length / session.questions.length) * 100
  );

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Question {currentIndex + 1} of {session.questions.length}
          </span>
          <span className="text-sm text-gray-600">
            {progress}% Complete
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question card */}
      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-lg font-medium">
            {currentQuestion.question}
          </h3>
          <button
            onClick={handleToggleFlag}
            className={`p-2 rounded-lg ${
              flagged.has(currentQuestion.id)
                ? 'bg-orange-100 text-orange-600'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <Flag size={20} />
          </button>
        </div>

        {/* Image (if present) */}
        {currentQuestion.image_url && (
          <img
            src={currentQuestion.image_url}
            alt="Question illustration"
            className="w-full rounded-lg mb-4"
          />
        )}

        {/* Options */}
        <div className="space-y-2">
          {Object.entries(currentQuestion.options).map(([key, value]) => (
            <button
              key={key}
              onClick={() => handleAnswerSelect(key)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedAnswer === key
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  selectedAnswer === key
                    ? 'border-primary-600 bg-primary-600'
                    : 'border-gray-300'
                }`}>
                  {selectedAnswer === key && (
                    <div className="w-2 h-2 bg-white rounded-full" />
                  )}
                </div>
                <div>
                  <span className="font-medium">{key}.</span> {value}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="btn-secondary flex items-center gap-2 disabled:opacity-50"
        >
          <ChevronLeft size={20} />
          Previous
        </button>

        {currentIndex === session.questions.length - 1 ? (
          <button
            onClick={handleFinish}
            className="btn-primary"
          >
            Finish Exam
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="btn-primary flex items-center gap-2"
          >
            Next
            <ChevronRight size={20} />
          </button>
        )}
      </div>
    </div>
  );
};

export default ExamQuestion;
```

**Exam Timer Component:**

```typescript
// src/components/exam/ExamTimer.tsx
import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';
import { ExamSession } from '../../types';

interface ExamTimerProps {
  session: ExamSession;
  onTimeUp: () => void;
}

const ExamTimer: React.FC<ExamTimerProps> = ({ session, onTimeUp }) => {
  const [remainingTime, setRemainingTime] = useState<number | null>(null);

  useEffect(() => {
    if (!session.timeLimit) return;

    const calculateRemaining = () => {
      const elapsed = Date.now() - session.startTime;
      const remaining = (session.timeLimit! * 1000) - elapsed;
      return Math.max(0, Math.floor(remaining / 1000));
    };

    setRemainingTime(calculateRemaining());

    const interval = setInterval(() => {
      const remaining = calculateRemaining();
      setRemainingTime(remaining);

      if (remaining === 0) {
        clearInterval(interval);
        onTimeUp();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [session, onTimeUp]);

  if (remainingTime === null) return null;

  const minutes = Math.floor(remainingTime / 60);
  const seconds = remainingTime % 60;
  const isLowTime = remainingTime < 60;

  return (
    <div className={`card mb-4 ${isLowTime ? 'bg-red-50 border-2 border-red-500' : ''}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isLowTime ? (
            <AlertTriangle className="text-red-600" size={20} />
          ) : (
            <Clock className="text-primary-600" size={20} />
          )}
          <span className="font-medium">
            {isLowTime ? 'Time Running Out!' : 'Time Remaining'}
          </span>
        </div>
        <div className={`text-2xl font-bold ${isLowTime ? 'text-red-600' : 'text-primary-600'}`}>
          {minutes}:{seconds.toString().padStart(2, '0')}
        </div>
      </div>
    </div>
  );
};

export default ExamTimer;
```

**Exam Results Component:**

```typescript
// src/components/exam/ExamResults.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useExamStore } from '../../store/examStore';
import { ExamSession } from '../../types';
import { Trophy, X, CheckCircle2, RotateCcw, Home } from 'lucide-react';

interface ExamResultsProps {
  session: ExamSession;
}

const ExamResults: React.FC<ExamResultsProps> = ({ session }) => {
  const navigate = useNavigate();
  const { clearSession } = useExamStore();

  const totalQuestions = session.questions.length;
  const correctAnswers = session.questions.filter(
    q => session.answers[q.id] === q.correct_answer
  ).length;
  const incorrectAnswers = Object.keys(session.answers).length - correctAnswers;
  const unanswered = totalQuestions - Object.keys(session.answers).length;

  const score = session.score || 0;
  const passed = score >= 60;

  const handleRetry = () => {
    clearSession();
  };

  const handleReview = () => {
    // Navigate to review page (to be implemented)
    alert('Review functionality coming soon');
  };

  const handleHome = () => {
    clearSession();
    navigate('/');
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <div className="card text-center">
        {/* Score display */}
        <div className="mb-6">
          <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${
            passed ? 'bg-green-100' : 'bg-red-100'
          }`}>
            {passed ? (
              <Trophy className="text-green-600" size={48} />
            ) : (
              <X className="text-red-600" size={48} />
            )}
          </div>
        </div>

        <h1 className={`text-4xl font-bold mb-2 ${passed ? 'text-green-600' : 'text-red-600'}`}>
          {score}%
        </h1>
        <p className="text-gray-600 mb-8">
          {passed ? 'Great job! You passed!' : 'Keep practicing!'}
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{correctAnswers}</div>
            <div className="text-sm text-gray-600">Correct</div>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{incorrectAnswers}</div>
            <div className="text-sm text-gray-600">Incorrect</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">{unanswered}</div>
            <div className="text-sm text-gray-600">Unanswered</div>
          </div>
        </div>

        {/* Question breakdown */}
        <div className="mb-8 space-y-2">
          {session.questions.map((question, index) => {
            const userAnswer = session.answers[question.id];
            const isCorrect = userAnswer === question.correct_answer;
            const wasAnswered = Boolean(userAnswer);

            return (
              <div
                key={question.id}
                className={`flex items-center justify-between p-3 rounded-lg ${
                  !wasAnswered
                    ? 'bg-gray-100'
                    : isCorrect
                    ? 'bg-green-50'
                    : 'bg-red-50'
                }`}
              >
                <span className="text-sm">Question {index + 1}</span>
                {wasAnswered ? (
                  isCorrect ? (
                    <CheckCircle2 className="text-green-600" size={20} />
                  ) : (
                    <X className="text-red-600" size={20} />
                  )
                ) : (
                  <span className="text-xs text-gray-500">Not answered</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button onClick={handleReview} className="btn-secondary flex-1">
            Review Answers
          </button>
          <button onClick={handleRetry} className="btn-primary flex-1 flex items-center justify-center gap-2">
            <RotateCcw size={20} />
            Try Again
          </button>
        </div>

        <button onClick={handleHome} className="btn-secondary w-full mt-4 flex items-center justify-center gap-2">
          <Home size={20} />
          Back to Home
        </button>
      </div>
    </div>
  );
};

export default ExamResults;
```

**Validation:**
- [ ] Exam starts with cached questions
- [ ] Timer counts down correctly (if enabled)
- [ ] Answers persist across page reloads (IndexedDB)
- [ ] Progress indicator updates in real-time
- [ ] Results page shows accurate statistics
- [ ] Mobile-friendly UI (all touch interactions work)

**Time Estimate:** 15 hours

---

### Task 6: Testing & Deployment (10 hours)

**Priority:** P1 (High - quality assurance)

**Mobile Device Testing Checklist:**

```bash
# Create testing checklist
cat > /home/dev/Development/irStudy/mobile-pwa/TESTING_CHECKLIST.md << 'EOF'
# Mobile PWA Testing Checklist

## iOS Testing (Safari)

### Installation
- [ ] Add to Home Screen works
- [ ] App icon appears correctly
- [ ] Splash screen displays
- [ ] App opens in standalone mode (no browser chrome)

### Functionality
- [ ] Search works (debounced input)
- [ ] AI chat responds within 3 seconds
- [ ] Exam mode loads questions
- [ ] Timer countdown works
- [ ] Offline mode works (airplane mode)

### UI/UX
- [ ] Safe area insets respected (notch/home indicator)
- [ ] Touch interactions responsive
- [ ] Swipe gestures don't interfere
- [ ] Font sizes readable
- [ ] Forms/inputs work correctly

## Android Testing (Chrome)

### Installation
- [ ] Install prompt appears
- [ ] App icon correct
- [ ] Splash screen displays
- [ ] Standalone mode works

### Functionality
- [ ] All features work as on iOS
- [ ] Service worker updates correctly
- [ ] IndexedDB persists data

### UI/UX
- [ ] Material Design patterns respected
- [ ] Back button behavior correct
- [ ] Navigation transitions smooth

## Performance

### Lighthouse Scores (Target)
- [ ] Performance: 90+
- [ ] Accessibility: 95+
- [ ] Best Practices: 90+
- [ ] SEO: 90+
- [ ] PWA: 100

### Network Performance
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Search response < 500ms
- [ ] AI response < 3s

## Offline Mode

- [ ] App loads without network
- [ ] Cached searches accessible
- [ ] Exam mode works offline
- [ ] Sync queue works when back online

## Edge Cases

- [ ] Low battery mode (iOS) doesn't break features
- [ ] Data saver mode (Android) works
- [ ] Slow 3G network handles gracefully
- [ ] Large datasets don't crash app
- [ ] Multiple tabs/windows sync correctly

EOF
```

**Lighthouse Performance Audit:**

```bash
# Install Lighthouse CI
cd /home/dev/Development/irStudy/mobile-pwa
npm install -D @lhci/cli

# Create Lighthouse config
cat > lighthouserc.json << 'EOF'
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run preview",
      "url": [
        "http://localhost:4173/",
        "http://localhost:4173/search",
        "http://localhost:4173/exam"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 0.9}],
        "categories:pwa": ["error", {"minScore": 1.0}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
EOF

# Run Lighthouse audit
npm run build
npx lhci autorun
```

**Vercel Deployment:**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to preview
cd /home/dev/Development/irStudy/mobile-pwa
vercel

# Expected output:
# 🔍  Inspect: https://vercel.com/...
# ✅  Preview: https://irstudy-mobile-xyz.vercel.app

# Deploy to production
vercel --prod

# Configure environment variables in Vercel dashboard:
# - VITE_API_URL=https://api.irstudy.com
```

**Create vercel.json config:**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "framework": "vite",
  "headers": [
    {
      "source": "/sw.js",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://api.irstudy.com/api/$1"
    }
  ]
}
```

**Continuous Integration (GitHub Actions):**

```yaml
# .github/workflows/pwa-deploy.yml
name: PWA Deploy

on:
  push:
    branches: [main]
    paths:
      - 'mobile-pwa/**'
  pull_request:
    branches: [main]
    paths:
      - 'mobile-pwa/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: mobile-pwa/package-lock.json

      - name: Install dependencies
        working-directory: mobile-pwa
        run: npm ci

      - name: Run tests
        working-directory: mobile-pwa
        run: npm test

      - name: Build
        working-directory: mobile-pwa
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.API_URL }}

      - name: Run Lighthouse CI
        working-directory: mobile-pwa
        run: |
          npm install -g @lhci/cli
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

      - name: Deploy to Vercel
        if: github.ref == 'refs/heads/main'
        working-directory: mobile-pwa
        run: |
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

**Final Validation Checklist:**

- [ ] Lighthouse scores meet targets (90+ across all categories)
- [ ] PWA installable on iOS and Android
- [ ] Offline mode fully functional
- [ ] Search response time < 500ms (p95)
- [ ] AI response time < 3 seconds (p95)
- [ ] All interactive elements accessible (keyboard + screen reader)
- [ ] Mobile-first design tested on real devices
- [ ] Production deployment successful
- [ ] Analytics/monitoring configured

**Time Estimate:** 10 hours

---

## 📊 Success Metrics

### Completion Criteria
- [ ] React PWA built with TypeScript + TailwindCSS
- [ ] RAG search integration functional (< 500ms response)
- [ ] AI clinical decision support working (Claude 3.5 Sonnet)
- [ ] Offline capability implemented (Service Worker + IndexedDB)
- [ ] Exam mode fully functional (timer, scoring, results)
- [ ] Deployed to Vercel with 90+ Lighthouse score
- [ ] Mobile-tested on iOS and Android devices

### Quality Gates
- [ ] Lighthouse Performance: 90+
- [ ] Lighthouse PWA: 100
- [ ] Search latency p95: < 500ms
- [ ] AI response latency p95: < 3s
- [ ] Code coverage: 80%+ (if tests implemented)
- [ ] Zero console errors in production

---

## 🔗 Related Documents

- **[README.md](./README.md)** - Overall feature modules plan
- **[02_PHASE2_EMR_PRACTICE.md](./02_PHASE2_EMR_PRACTICE.md)** - Next phase
- **[/home/dev/Development/irStudy/constraints/README.md](../../constraints/README.md)** - Project constraints

---

## 📞 Support

**Questions?** Review existing codebase:
- **MCQ App:** `/home/dev/Development/irStudy/respiratory-mcq-app/src/app.js`
- **RAG Client:** `/home/dev/Development/irStudy/src/rag/qdrant_client.py`
- **LLM Integration:** `/home/dev/Development/irStudy/src/llm/`

**Blockers?** Ensure prerequisites are met:
- Qdrant running on localhost:6333
- Anthropic API key configured
- Node.js 18+ installed

---

**Last Updated:** 2026-02-01
**Owner:** Frontend Developer
**Estimated Completion:** 2026-02-15 (2 weeks)
