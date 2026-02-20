# PRD: TASK_009 - Mobile Responsive Design & PWA
**Product Requirements Document**

---

## Document Metadata
- **PRD ID**: TASK_009
- **Product Name**: irStudy - AMC Medical Education Platform
- **Feature**: Mobile Responsive Design + Progressive Web App (PWA)
- **Version**: 1.0
- **Date**: 2026-02-15
- **Author**: Project Manager Coordinator
- **Status**: Ready for Implementation
- **Priority**: P0 (Critical - Accessibility & Mobile-First)

---

## Executive Summary

### Problem Statement
Medical students study on-the-go using mobile devices (phones, tablets) but the current irStudy platform is desktop-only (0% mobile implementation). This limits accessibility and prevents students from practicing during commutes, breaks, or away from computers.

### Solution Overview
Transform irStudy into a mobile-first, Progressive Web App (PWA) with:
- Responsive breakpoints (mobile 320px, tablet 768px, desktop 1024px+)
- Mobile bottom navigation (replaces sidebar on small screens)
- Touch-optimized interactions (≥44x44px touch targets)
- PWA configuration (offline support, installable, app-like experience)
- Swipe gestures for quiz navigation
- Lighthouse score >90 (Performance, Accessibility, Best Practices, PWA)

### Success Metrics
- **Mobile Usage**: >50% of practice sessions from mobile devices
- **PWA Installation**: >30% of mobile users install PWA
- **Lighthouse Score**: >90 (all metrics)
- **Touch Target Compliance**: 100% interactive elements ≥44x44px
- **Load Time**: <2s on 3G network (mobile)

---

## User Stories & Requirements

### US-009-001: Responsive Breakpoints
**As a** medical student
**I want to** use irStudy on any device (phone, tablet, desktop)
**So that** I can study anywhere, anytime

**Acceptance Criteria**:
- [ ] 5 responsive breakpoints defined:
  - xs: 320px (Mobile small - iPhone SE)
  - sm: 768px (Tablet portrait - iPad)
  - md: 1024px (Tablet landscape / Desktop small)
  - lg: 1280px (Desktop)
  - xl: 1920px (Desktop XL)
- [ ] All components responsive at each breakpoint
- [ ] Grid layouts adapt (1 col → 2 col → 4 col)
- [ ] Typography scales appropriately
- [ ] Images optimize for viewport

**Material-UI Theme Configuration**:
```typescript
// frontend/src/theme/theme.ts
export const theme = createTheme({
  breakpoints: {
    values: {
      xs: 320,   // Mobile small
      sm: 768,   // Tablet portrait
      md: 1024,  // Tablet landscape / Desktop small
      lg: 1280,  // Desktop
      xl: 1920,  // Desktop XL
    },
  },
  typography: {
    h4: {
      fontSize: {
        xs: '1.5rem',  // Mobile
        sm: '1.75rem', // Tablet
        md: '2rem',    // Desktop
      },
    },
  },
});
```

**Responsive Grid Usage**:
```typescript
<Grid container spacing={{ xs: 1, sm: 2, md: 3 }}>
  <Grid item xs={12} sm={6} md={3}>
    {/* Stack on mobile (xs=12), 2 cols on tablet (sm=6), 4 cols on desktop (md=3) */}
    <StatCard />
  </Grid>
</Grid>
```

---

### US-009-002: Mobile Bottom Navigation
**As a** mobile user
**I want to** navigate using bottom navigation bar
**So that** I can easily access key features with my thumb

**Acceptance Criteria**:
- [ ] Bottom navigation shown on mobile (<768px)
- [ ] 4 navigation items: Home, Practice, Dashboard, Profile
- [ ] Active item highlighted
- [ ] Fixed to bottom of screen
- [ ] Touch targets ≥56px height
- [ ] Smooth transitions between pages
- [ ] Hidden on desktop (sidebar shown instead)

**Component Implementation**:
```typescript
// frontend/src/components/layout/MobileBottomNav.tsx (NEW)
import { BottomNavigation, BottomNavigationAction } from '@mui/material';
import { Home, Quiz, Dashboard, Person } from '@mui/icons-material';

export const MobileBottomNav: React.FC = () => {
  const [value, setValue] = useState('home');
  const navigate = useNavigate();
  const { isMobile } = useResponsive();

  if (!isMobile) return null;  // Hide on desktop

  return (
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue);
        navigate(`/${newValue}`);
      }}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: 56,  // Thumb-friendly height
        borderTop: '1px solid',
        borderColor: 'divider',
        zIndex: 1000,
      }}
    >
      <BottomNavigationAction
        label="Home"
        value="home"
        icon={<Home />}
      />
      <BottomNavigationAction
        label="Practice"
        value="practice"
        icon={<Quiz />}
      />
      <BottomNavigationAction
        label="Dashboard"
        value="dashboard"
        icon={<Dashboard />}
      />
      <BottomNavigationAction
        label="Profile"
        value="profile"
        icon={<Person />}
      />
    </BottomNavigation>
  );
};
```

---

### US-009-003: Touch-Optimized Interactions
**As a** mobile user
**I want to** easily tap buttons and interactive elements
**So that** I don't misclick due to small touch targets

**Acceptance Criteria**:
- [ ] All buttons ≥44x44px (WCAG 2.2 Level AAA)
- [ ] Radio buttons ≥44x44px touch area
- [ ] Links ≥44x44px
- [ ] Interactive elements have 8px spacing
- [ ] Hover states replaced with active states on touch devices
- [ ] No reliance on hover-only interactions

**Material-UI Theme (Touch Targets)**:
```typescript
// theme.ts
components: {
  MuiButton: {
    styleOverrides: {
      root: {
        minHeight: 44,
        minWidth: 44,
        padding: '8px 16px',
      },
    },
  },
  MuiIconButton: {
    styleOverrides: {
      root: {
        minHeight: 44,
        minWidth: 44,
      },
    },
  },
  MuiFormControlLabel: {
    styleOverrides: {
      root: {
        minHeight: 44,
      },
    },
  },
}
```

**Touch Area Expansion**:
```typescript
// For small visual elements, expand touch area invisibly
<IconButton
  sx={{
    padding: '12px',  // Creates 44x44px touch area even if icon is 20x20px
  }}
>
  <InfoIcon />
</IconButton>
```

---

### US-009-004: Swipe Gestures
**As a** mobile user
**I want to** swipe to navigate between MCQ questions
**So that** I can practice efficiently without tapping buttons

**Acceptance Criteria**:
- [ ] Swipe left: Next question (after submission)
- [ ] Swipe right: New question / retry (before submission)
- [ ] Visual hint for swipe actions (first time user)
- [ ] Swipe distance threshold: 80px minimum
- [ ] Vertical scrolling unaffected
- [ ] Works on touch devices only (not desktop)

**Implementation**:
```typescript
// Using react-swipeable library
import { useSwipeable } from 'react-swipeable';

export const MCQPracticeInterface: React.FC = () => {
  const { isMobile } = useResponsive();

  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (isMobile && isSubmitted) {
        handleNext();  // Next question
      }
    },
    onSwipedRight: () => {
      if (isMobile && !isSubmitted) {
        refetch();  // New question
      }
    },
    preventScrollOnSwipe: false,  // Allow vertical scrolling
    delta: 80,  // Minimum swipe distance (px)
    trackMouse: false,  // Touch only, not mouse
  });

  return (
    <Card {...swipeHandlers}>
      {/* MCQ content */}
    </Card>
  );
};
```

---

### US-009-005: Progressive Web App (PWA)
**As a** mobile user
**I want to** install irStudy as a native app
**So that** I can access it quickly from my home screen and use offline

**Acceptance Criteria**:
- [ ] PWA installable on mobile (iOS, Android)
- [ ] App manifest configured (name, icons, theme color)
- [ ] Service worker for offline support
- [ ] Cached assets (HTML, CSS, JS, images)
- [ ] Offline fallback page
- [ ] "Add to Home Screen" prompt
- [ ] Splash screen on iOS/Android
- [ ] Lighthouse PWA score: 100

**Vite PWA Configuration**:
```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'irStudy - AMC Medical Education',
        short_name: 'irStudy',
        description: 'Australian Medical Council (AMC) Exam Preparation Platform',
        theme_color: '#1976d2',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,jpg,jpeg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.irstudy\.com\/api\/v1\/.*/i,
            handler: 'NetworkFirst',  // Try network first, fallback to cache
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24,  // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
    }),
  ],
});
```

**App Manifest**:
```json
// public/manifest.webmanifest
{
  "name": "irStudy - AMC Medical Education",
  "short_name": "irStudy",
  "description": "Australian Medical Council exam preparation with MCQ, OSCE, and Study Cards",
  "theme_color": "#1976d2",
  "background_color": "#ffffff",
  "display": "standalone",
  "scope": "/",
  "start_url": "/",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/pwa-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/pwa-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

### US-009-006: Responsive Dashboard Charts
**As a** mobile user
**I want to** view performance charts optimized for small screens
**So that** I can track my progress on mobile devices

**Acceptance Criteria**:
- [ ] Charts resize for mobile (reduced height)
- [ ] Fewer data points on mobile (4 weeks vs 12 weeks)
- [ ] Axis labels rotate/abbreviate on mobile
- [ ] Legend hidden on mobile (to save space)
- [ ] Horizontal scroll for wide charts (if needed)
- [ ] Touch-friendly tooltips

**Implementation**:
```typescript
// frontend/src/components/dashboard/PerformanceChart.tsx (RESPONSIVE)
export const PerformanceChart: React.FC<{ trends: WeeklyTrend[] }> = ({ trends }) => {
  const { isMobile } = useResponsive();

  // Adjust dimensions
  const chartHeight = isMobile ? 200 : 300;
  const margin = isMobile
    ? { top: 5, right: 10, left: 10, bottom: 5 }
    : { top: 5, right: 30, left: 20, bottom: 5 };

  // Show fewer data points on mobile
  const displayTrends = isMobile ? trends.slice(-4) : trends;

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <LineChart data={displayTrends} margin={margin}>
        <XAxis
          dataKey="week"
          tick={{ fontSize: isMobile ? 10 : 12 }}
          angle={isMobile ? -45 : 0}  // Rotate labels on mobile
          textAnchor={isMobile ? 'end' : 'middle'}
        />
        <YAxis tick={{ fontSize: isMobile ? 10 : 12 }} />
        <Tooltip />
        {!isMobile && <Legend />}  {/* Hide legend on mobile */}
        <Line
          type="monotone"
          dataKey="accuracy"
          stroke="#8884d8"
          strokeWidth={isMobile ? 1.5 : 2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

---

### US-009-007: Lighthouse Optimization
**As a** developer
**I want to** achieve Lighthouse scores >90 (all metrics)
**So that** irStudy meets industry-standard performance and quality

**Acceptance Criteria**:
- [ ] Lighthouse Performance: >90
- [ ] Lighthouse Accessibility: >95 (WCAG 2.2 AA)
- [ ] Lighthouse Best Practices: >90
- [ ] Lighthouse SEO: >90
- [ ] Lighthouse PWA: 100

**Optimization Techniques**:

1. **Code Splitting (Lazy Loading)**:
```typescript
// App.tsx
const PerformanceDashboard = lazy(() => import('@/pages/PerformanceDashboard'));
const MCQPracticePage = lazy(() => import('@/pages/MCQPracticePage'));

function App() {
  return (
    <Suspense fallback={<CircularProgress />}>
      <Routes>
        <Route path="/dashboard" element={<PerformanceDashboard />} />
        <Route path="/practice/mcq" element={<MCQPracticePage />} />
      </Routes>
    </Suspense>
  );
}
```

2. **Image Optimization**:
```typescript
<img
  src="/medical-image.jpg"
  alt="ECG showing sinus rhythm"
  loading="lazy"  // Lazy load offscreen images
  width={600}
  height={400}  // Prevent layout shift
/>
```

3. **Font Optimization (Preload)**:
```html
<link
  rel="preload"
  href="/fonts/roboto-v30-latin-regular.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

4. **Bundle Size Reduction**:
- Main bundle: <500KB (gzipped)
- Lazy-loaded routes: <150KB each
- Total initial load: <800KB

**Lighthouse Audit Command**:
```bash
# Build production
npm run build

# Serve production build
npx vite preview --port 4173

# Run Lighthouse (mobile)
npx lighthouse http://localhost:4173 \
  --preset=mobile \
  --output html \
  --output-path reports/lighthouse-mobile.html \
  --view

# Run Lighthouse (desktop)
npx lighthouse http://localhost:4173 \
  --preset=desktop \
  --output html \
  --output-path reports/lighthouse-desktop.html \
  --view
```

---

## Technical Specifications

### useResponsive Hook

```typescript
// frontend/src/hooks/useResponsive.ts (NEW)
import { useTheme, useMediaQuery } from '@mui/material';

export const useResponsive = () => {
  const theme = useTheme();

  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));  // <768px
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));  // 768-1024px
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));  // ≥1024px

  return { isMobile, isTablet, isDesktop };
};
```

### Responsive Sidebar

```typescript
// frontend/src/components/layout/Sidebar.tsx (ENHANCE)
export const Sidebar: React.FC = () => {
  const { isMobile } = useResponsive();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile: Temporary drawer */}
      {isMobile ? (
        <Drawer
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          variant="temporary"
          ModalProps={{ keepMounted: true }}  // Better performance
        >
          <SidebarContent />
        </Drawer>
      ) : (
        /* Desktop: Permanent drawer */
        <Drawer variant="permanent" open>
          <SidebarContent />
        </Drawer>
      )}
    </>
  );
};
```

---

## Testing Requirements

### Responsive Testing

**Coverage Target**: 70%+

**Test Cases**:
```typescript
describe('Mobile Responsive Layout', () => {
  it('shows bottom navigation on mobile', () => {
    window.matchMedia = createMatchMedia(360);  // Mobile width

    render(<App />);
    expect(screen.getByRole('navigation', { name: /bottom/i })).toBeVisible();
  });

  it('hides bottom navigation on desktop', () => {
    window.matchMedia = createMatchMedia(1280);  // Desktop width

    render(<App />);
    expect(screen.queryByRole('navigation', { name: /bottom/i })).not.toBeInTheDocument();
  });

  it('stacks stat cards on mobile', () => {
    window.matchMedia = createMatchMedia(360);

    render(<PerformanceDashboard />);

    const statCards = screen.getAllByTestId('stat-card');
    statCards.forEach((card) => {
      expect(card.parentElement).toHaveClass('MuiGrid-grid-xs-12');
    });
  });
});
```

### E2E Mobile Testing (Playwright)

```typescript
// testing/playwright/tests/mobile/mcq-practice-mobile.spec.ts
import { test, expect, devices } from '@playwright/test';

test.use(devices['iPhone 12']);  // Mobile device emulation

test('MCQ practice on mobile', async ({ page }) => {
  await page.goto('/practice/mcq');

  // Verify bottom navigation visible
  await expect(page.locator('[role="navigation"]').last()).toBeVisible();

  // Test swipe gesture
  const mcqCard = page.locator('[data-testid="mcq-card"]');
  await mcqCard.swipe({ direction: 'left' });

  // Verify next question loaded
  await expect(page.locator('[data-testid="mcq-question"]')).toBeVisible();
});

test('Dashboard responsive on mobile', async ({ page }) => {
  await page.goto('/dashboard');

  // Verify stacked layout
  const viewport = page.viewportSize();
  expect(viewport?.width).toBe(390);  // iPhone 12 width

  // Verify charts render at mobile height
  const chart = page.locator('canvas').first();
  const bbox = await chart.boundingBox();
  expect(bbox?.height).toBeLessThan(250);  // Mobile chart height
});
```

### PWA Testing

**Test Cases**:
1. ✅ Manifest valid (Chrome DevTools > Application > Manifest)
2. ✅ Service worker registered (Application > Service Workers)
3. ✅ Offline mode works (Network > Offline)
4. ✅ "Add to Home Screen" prompt shown
5. ✅ App installable on mobile devices
6. ✅ Lighthouse PWA score: 100

---

## Success Criteria

### Functional Requirements
- ✅ Mobile breakpoints work (320px, 768px, 1024px)
- ✅ Bottom navigation on mobile (<768px)
- ✅ Sidebar drawer on mobile
- ✅ Touch targets ≥44x44px (100% compliance)
- ✅ Swipe gestures functional (MCQ practice)
- ✅ PWA installable on iOS and Android
- ✅ Offline mode functional

### Quality Requirements
- ✅ Lighthouse Performance: >90
- ✅ Lighthouse Accessibility: >95
- ✅ Lighthouse Best Practices: >90
- ✅ Lighthouse SEO: >90
- ✅ Lighthouse PWA: 100
- ✅ Test coverage ≥70%
- ✅ Load time <2s on 3G

### User Metrics
- ✅ >50% practice sessions from mobile
- ✅ >30% mobile users install PWA
- ✅ <5% mobile bounce rate
- ✅ User satisfaction >4.5/5 (mobile)

---

## Implementation Timeline

**Sprint 3 - Week 3 (6 hours)**

**Days 1-2 (6 hours)**:
- Configure theme breakpoints
- Create MobileBottomNav component
- Make Sidebar responsive (drawer on mobile)
- Implement useResponsive() hook
- Add swipe gestures

**Days 3-4 (6 hours)**:
- Configure PWA (Vite plugin, manifest)
- Create service worker caching strategy
- Optimize images (lazy loading)
- Code splitting for routes
- Run Lighthouse audits and optimize

**Day 5 (2 hours)**:
- E2E mobile testing (Playwright device emulation)
- Cross-browser testing (Chrome, Safari, Firefox)
- Final Lighthouse audit (target >90 all metrics)
- Mark TASK_009 complete

---

## Risks & Mitigations

### Risk 1: Mobile Performance
**Probability**: Medium
**Impact**: High
**Mitigation**: Reduce data points on mobile, optimize images, code splitting, Lighthouse audits

### Risk 2: iOS PWA Limitations
**Probability**: High
**Impact**: Medium
**Mitigation**: Test on real iOS devices, document limitations, fallback to web app

### Risk 3: Touch Target Compliance
**Probability**: Low
**Impact**: Medium
**Mitigation**: Material-UI theme enforces 44px minimum, accessibility tests verify

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2026-02-15
