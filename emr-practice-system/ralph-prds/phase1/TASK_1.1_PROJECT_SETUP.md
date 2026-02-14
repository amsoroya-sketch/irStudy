# RALPH Task 1.1 - Frontend Project Setup

**Phase**: 1 - Frontend Implementation
**Task**: 1.1
**Estimated Time**: 4 hours
**Agent**: general-purpose
**Status**: Ready for execution

---

## Task Overview

Setup React + TypeScript + Vite project for EMR practice system frontend with all dependencies, Tailwind CSS configuration, and project structure.

---

## Context

You are setting up a **NEW** frontend module for the EMR practice system. This will be a separate React application that integrates with the main irStudy platform but runs independently during development.

**Important**: This is NOT modifying the existing `/home/dev/Development/irStudy/frontend` directory. We're creating a NEW directory `/home/dev/Development/irStudy/emr-frontend`.

---

## Requirements

### 1. Create Project Directory

```bash
cd /home/dev/Development/irStudy
npm create vite@latest emr-frontend -- --template react-ts
cd emr-frontend
```

### 2. Install Core Dependencies

```bash
npm install react@18.2.0 react-dom@18.2.0
npm install -D typescript@5.3.3 @types/react@18.2.48 @types/react-dom@18.2.18
npm install -D vite@5.0.10 @vitejs/plugin-react@4.2.1
```

### 3. Install UI & Styling Dependencies

```bash
npm install tailwindcss@3.4.1 postcss@8.4.33 autoprefixer@10.4.17
npm install framer-motion@11.0.3
npm install lucide-react@0.309.0
npm install -D @types/node
```

### 4. Install Form & Validation Dependencies

```bash
npm install react-hook-form@7.49.3
npm install zod@3.22.4
npm install @hookform/resolvers@3.3.4
```

### 5. Install State Management

```bash
npm install @tanstack/react-query@5.17.15
npm install zustand@4.4.7
```

### 6. Install Utility Dependencies

```bash
npm install axios@1.6.5
npm install date-fns@3.2.0
npm install clsx@2.1.0
npm install tailwind-merge@2.2.0
```

### 7. Configure Tailwind CSS

Create `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cerner theme colors
        'cerner-primary': '#3498db',
        'cerner-bg-dark': '#2c3e50',
        'cerner-bg-darker': '#1a252f',
        'cerner-success': '#27ae60',
        'cerner-error': '#e74c3c',

        // Epic theme colors
        'epic-primary': '#8b5cf6',
        'epic-primary-dark': '#7c3aed',
        'epic-bg-white': '#ffffff',
        'epic-bg-light': '#f9fafb',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

Create `postcss.config.js`:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Update `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Cerner theme variables */
:root[data-theme="cerner"] {
  --cerner-primary: #3498db;
  --cerner-bg-dark: #2c3e50;
  --cerner-bg-darker: #1a252f;
  --cerner-success: #27ae60;
  --cerner-error: #e74c3c;
  --cerner-warning: #f39c12;
}

/* Epic theme variables */
:root[data-theme="epic"] {
  --epic-primary: #8b5cf6;
  --epic-primary-dark: #7c3aed;
  --epic-bg-white: #ffffff;
  --epic-bg-light: #f9fafb;
}

/* Base styles */
body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}
```

### 8. Create Folder Structure

```bash
cd src
mkdir -p components/{cerner,epic,shared}
mkdir -p pages/{dashboard,cerner,epic}
mkdir -p hooks
mkdir -p stores
mkdir -p api/{client,hooks}
mkdir -p schemas
mkdir -p utils
mkdir -p types
mkdir -p styles
```

Final structure:
```
src/
├── components/
│   ├── cerner/          # Cerner PowerChart components
│   ├── epic/            # Epic EHR components
│   └── shared/          # Shared components
├── pages/
│   ├── dashboard/       # Dashboard pages
│   ├── cerner/          # Cerner pages
│   └── epic/            # Epic pages
├── hooks/               # Custom React hooks
├── stores/              # Zustand stores
├── api/
│   ├── client/          # Axios client setup
│   └── hooks/           # TanStack Query hooks
├── schemas/             # Zod validation schemas
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
└── styles/              # Global styles
```

### 9. Configure Vite

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@api': path.resolve(__dirname, './src/api'),
      '@schemas': path.resolve(__dirname, './src/schemas'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
    },
  },
  server: {
    port: 5174,  // Different from main frontend (5173)
    proxy: {
      '/api': {
        target: 'http://localhost:8001',  // Backend API
        changeOrigin: true,
      },
    },
  },
})
```

Update `tsconfig.json` to include path aliases:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@stores/*": ["./src/stores/*"],
      "@api/*": ["./src/api/*"],
      "@schemas/*": ["./src/schemas/*"],
      "@utils/*": ["./src/utils/*"],
      "@types/*": ["./src/types/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 10. Create Environment Configuration

Create `.env.example`:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8001/api/v1

# Anthropic API Key (for AI validation - backend will use this)
VITE_ANTHROPIC_API_KEY=

# Session timeout (minutes)
VITE_SESSION_TIMEOUT=15

# Auto-save interval (seconds)
VITE_AUTO_SAVE_INTERVAL=30

# Environment
VITE_ENV=development
```

Create `.env` (gitignored):

```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_SESSION_TIMEOUT=15
VITE_AUTO_SAVE_INTERVAL=30
VITE_ENV=development
```

### 11. Update package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  }
}
```

### 12. Create Basic App Component

Update `src/App.tsx`:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const [theme, setTheme] = useState<'cerner' | 'epic'>('cerner');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100" data-theme={theme}>
        <header className="bg-white shadow-sm p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              EMR Practice System
            </h1>
            <div className="flex gap-4">
              <button
                onClick={() => setTheme('cerner')}
                className={`px-4 py-2 rounded ${
                  theme === 'cerner'
                    ? 'bg-cerner-primary text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Cerner
              </button>
              <button
                onClick={() => setTheme('epic')}
                className={`px-4 py-2 rounded ${
                  theme === 'epic'
                    ? 'bg-epic-primary text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Epic
              </button>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto p-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              Welcome to EMR Practice System
            </h2>
            <p className="text-gray-600">
              Project setup complete! Ready for component implementation.
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <p className="font-mono text-sm">
                Current theme: <strong>{theme}</strong>
              </p>
            </div>
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
```

---

## References

- **Master PRD**: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md` (section 5.1)
- **Styling Spec**: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md` (sections 1-2)

---

## Validation Checklist

Before marking this task complete, verify:

- [ ] `npm run dev` starts successfully on port 5174
- [ ] Browser shows "Welcome to EMR Practice System" message
- [ ] Tailwind CSS classes work (theme toggle buttons styled correctly)
- [ ] Theme toggle works (Cerner blue vs Epic purple)
- [ ] TypeScript compilation has 0 errors (`npm run type-check`)
- [ ] All dependencies installed (`node_modules` exists)
- [ ] All folders created in `src/` directory
- [ ] `.env` file created with values
- [ ] Path aliases work (no import errors)
- [ ] No console errors in browser
- [ ] Hot module reload works (edit App.tsx, auto-refreshes)

### Test Commands

```bash
# 1. Check TypeScript compilation
npm run type-check
# Expected: No errors

# 2. Start dev server
npm run dev
# Expected: Server starts on http://localhost:5174

# 3. Check folder structure
ls -la src/
# Expected: All folders listed above exist

# 4. Verify dependencies
npm list --depth=0
# Expected: All packages from requirements listed
```

---

## Deliverable

A working Vite + React + TypeScript project with:
- ✅ All dependencies installed
- ✅ Tailwind CSS configured with Cerner & Epic themes
- ✅ Folder structure created
- ✅ Vite config with API proxy
- ✅ TypeScript path aliases
- ✅ Environment variables setup
- ✅ Basic App component with theme toggle
- ✅ Development server running on port 5174

---

## Troubleshooting

### Issue: Port 5174 already in use
```bash
# Solution: Kill process or use different port
lsof -ti:5174 | xargs kill -9
# Or edit vite.config.ts and change port
```

### Issue: TypeScript errors with path aliases
```bash
# Solution: Restart VS Code / restart TypeScript server
# Or verify tsconfig.json baseUrl and paths are correct
```

### Issue: Tailwind classes not working
```bash
# Solution: Verify tailwind.config.js content paths include src/**
# Restart dev server: Ctrl+C, then npm run dev
```

---

## Next Steps

After this task is complete and validated:
- **Task 1.2**: Implement Cerner UI components (5 components, 16 hours)
- **RALPH PRD**: `ralph-prds/phase1/TASK_1.2_CERNER_COMPONENTS.md`

---

**Task Status**: Ready for execution
**Estimated Time**: 4 hours
**Complexity**: Low
**Dependencies**: None

