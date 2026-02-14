# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_009 - Mobile Responsive Design (4-5 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/frontend

# Configure mobile breakpoints in theme
cat > src/theme/theme.ts <<'EOF'
// Theme configuration will be implemented here
EOF

# Install Lighthouse CLI
npm install -D lighthouse

# Run Lighthouse audit
npx lighthouse http://localhost:5173 --output html --output-path lighthouse-report.html --view
```

**DO NOT**:
- ❌ Ask "Would you like me to implement PWA features?"
- ❌ Ask "Should I use a specific breakpoint system?"
- ❌ Wait for approval
- ❌ Ask "Which service worker strategy should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 2
- **Day:** 5 (Feb 18, 2026)
- **Duration:** 4-5 hours
- **Priority:** P1-High
- **Dependencies:** TASK_006 (Quiz Interface), TASK_008 (Dashboard)
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_010 (E2E Testing)

---

## 🎯 Objectives

1. **Implement mobile breakpoints** (320px, 768px, 1024px)
2. **Create touch-optimized UI** (flashcard flip gesture, quiz tap)
3. **Configure PWA** (Progressive Web App)
4. **Implement service worker** (offline-first strategy)
5. **Achieve Lighthouse score >90** on mobile
6. **Verify all pages responsive**

---

## 📝 Implementation Guide

### Step 1: Configure Material-UI Theme with Breakpoints (30 min)

```bash
cat > src/theme/theme.ts <<'EOF'
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  breakpoints: {
    values: {
      xs: 320,  // Mobile small
      sm: 768,  // Tablet
      md: 1024, // Desktop small
      lg: 1280, // Desktop large
      xl: 1920  // Desktop XL
    }
  },
  palette: {
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#dc004e'
    }
  },
  typography: {
    h4: {
      fontSize: '2rem',
      '@media (max-width:768px)': {
        fontSize: '1.5rem'
      }
    },
    h6: {
      fontSize: '1.25rem',
      '@media (max-width:768px)': {
        fontSize: '1rem'
      }
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          '@media (max-width:768px)': {
            fontSize: '0.875rem',
            padding: '8px 16px'
          }
        }
      }
    }
  }
});
EOF

# Update App.tsx to use theme
cat > src/App.tsx <<'EOF'
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './theme/theme';
import { DashboardPage } from './pages/DashboardPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <DashboardPage />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
EOF
```

### Step 2: Add Responsive Utilities & Touch Gestures (1.5 hours)

```bash
cat > src/hooks/useResponsive.ts <<'EOF'
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

export const useResponsive = () => {
  const theme = useTheme();

  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));  // <768px
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));  // 768-1024px
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));  // >1024px

  return { isMobile, isTablet, isDesktop };
};
EOF

# Update MCQ Practice Interface for mobile
cat >> src/components/mcq/MCQPracticeInterface.tsx <<'EOF'
// Add mobile-specific imports at top
import { useResponsive } from '../../hooks/useResponsive';
import { useSwipeable } from 'react-swipeable';

// Inside component, add:
const { isMobile } = useResponsive();

// Swipe handlers for mobile navigation
const swipeHandlers = useSwipeable({
  onSwipedLeft: () => isMobile && handleNext(),
  onSwipedRight: () => isMobile && refetch(),
  preventDefaultTouchmoveEvent: true,
  trackMouse: false
});

// Update Box wrapper to include swipe handlers
<Box {...swipeHandlers} sx={{ maxWidth: isMobile ? '100%' : 900, padding: isMobile ? 2 : 3 }}>
EOF

npm install react-swipeable
```

### Step 3: Configure PWA (1 hour)

```bash
# Install Vite PWA plugin
npm install -D vite-plugin-pwa

# Update vite.config.ts
cat > vite.config.ts <<'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'irStudy Medical Education',
        short_name: 'irStudy',
        description: 'Australian Medical Council (AMC) Exam Preparation',
        theme_color: '#1976d2',
        background_color: '#ffffff',
        display: 'standalone',
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
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,jpg,jpeg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.irstudy\.com\/api\/v1\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24  // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ]
});
EOF
```

### Step 4: Optimize for Mobile Performance (1 hour)

```bash
# Create lazy loading for routes
cat > src/routes.tsx <<'EOF'
import { lazy, Suspense } from 'react';
import { CircularProgress, Box } from '@mui/material';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const MCQPracticePage = lazy(() => import('./pages/MCQPracticePage'));

const LoadingFallback = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
    <CircularProgress />
  </Box>
);

export const AppRoutes = () => (
  <Suspense fallback={<LoadingFallback />}>
    {/* Route definitions here */}
  </Suspense>
);
EOF

# Add viewport meta tag in index.html
cat > index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes" />
    <meta name="description" content="Australian Medical Council (AMC) Exam Preparation Platform" />
    <meta name="theme-color" content="#1976d2" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/manifest.webmanifest" />
    <title>irStudy Medical Education</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
```

### Step 5: Run Lighthouse Audit & Optimize (1 hour)

```bash
# Build production version
npm run build

# Serve production build
npx vite preview --port 4173 &

# Run Lighthouse audit
npx lighthouse http://localhost:4173 --output html --output-path lighthouse-mobile.html --preset=mobile --view

# Run desktop audit
npx lighthouse http://localhost:4173 --output html --output-path lighthouse-desktop.html --preset=desktop --view

# Expected scores: >90 for performance, accessibility, best practices, SEO
```

---

## ✅ Validation Checklist

```bash
cd /home/dev/Development/irStudy/frontend

# 1. Verify theme configuration
[ -f src/theme/theme.ts ] && echo "✅ Theme: EXISTS" || echo "❌ MISSING"

# 2. Verify responsive hook
[ -f src/hooks/useResponsive.ts ] && echo "✅ Responsive hook: EXISTS" || echo "❌ MISSING"

# 3. Verify PWA configuration
grep -q "VitePWA" vite.config.ts && echo "✅ PWA: CONFIGURED" || echo "❌ NOT CONFIGURED"

# 4. Check viewport meta tag
grep -q "viewport" index.html && echo "✅ Viewport: CONFIGURED" || echo "❌ MISSING"

# 5. Run TypeScript check
npx tsc --noEmit && echo "✅ TypeScript: 0 errors" || echo "❌ TypeScript errors"

# 6. Run Lighthouse audit (manual verification)
echo "Run: npm run build && npx vite preview --port 4173"
echo "Then: npx lighthouse http://localhost:4173 --preset=mobile"
echo "Expected: Score >90"
```

---

## 🎯 Success Criteria

1. ✅ Mobile breakpoints implemented (320px, 768px, 1024px)
2. ✅ Touch-optimized UI (swipe gestures functional)
3. ✅ PWA configured (manifest + service worker)
4. ✅ Service worker implemented (offline-first)
5. ✅ Lighthouse score >90 on mobile
6. ✅ All pages mobile-responsive

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

sed -i 's/TASK_009.*TODO/TASK_009: ✅ DONE/' @fix_plan.md

git add .
git commit -m "feat(frontend): Complete TASK_009 Mobile Responsive Design - PWA + Lighthouse >90

- Mobile breakpoints: 320px, 768px, 1024px
- Touch-optimized UI with swipe gestures
- PWA configuration with service worker
- Offline-first caching strategy
- Lighthouse score: >90 (mobile + desktop)
- All pages responsive

Deliverables:
- frontend/src/theme/theme.ts
- frontend/src/hooks/useResponsive.ts
- frontend/vite.config.ts (PWA plugin)
- frontend/index.html (viewport meta)
- lighthouse-mobile.html (audit report)

Quality Gates: 6/6 passed ✅
Blocks: TASK_010 now unblocked (Week 3 begins)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_009 complete. Week 2 frontend tasks finished!"
echo "Next: TASK_010 (Week 3 - Integration & Polish)"
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_006, TASK_008
**Blocks:** TASK_010
