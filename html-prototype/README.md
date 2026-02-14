# irStudy UI Prototypes

Complete HTML-only UI prototypes for all irStudy platform modules with dummy data. Ready for review before integration.

## 🚀 Quick Start

**Open `index.html`** in your browser to see the navigation hub with all prototypes.

## 📁 Structure

```
html-prototype/
├── index.html              # Main navigation hub
├── README.md               # This file
├── css/
│   └── design-system.css   # Shared CSS variables and utilities
├── web/                    # Web Application (Desktop)
│   ├── index.html          # Landing page with marketing
│   ├── auth.html           # Login/Register
│   ├── dashboard.html      # Main dashboard with sidebar
│   ├── mcq-study.html      # MCQ question interface
│   ├── osce-practice.html  # OSCE scenario with chat
│   ├── osce-feedback.html  # AI examiner feedback
│   ├── emr-simulation.html # EMR (Cerner dark theme)
│   ├── analytics.html      # Progress & analytics
│   ├── bookmarks.html      # Bookmarks & notes
│   ├── study-plan.html     # Study plan & schedule
│   └── settings.html       # Account settings
├── mobile/                 # Mobile Application
│   ├── index.html          # Mobile dashboard
│   ├── mcq.html            # Full-screen MCQ
│   ├── osce.html           # Audio-first OSCE
│   └── emr.html            # Mobile EMR
├── tablet/                 # Tablet Layout
│   └── index.html          # Collapsible sidebar layout
└── desktop/                # Desktop App (Tauri)
    ├── index.html          # Desktop home
    ├── exam-mode.html      # Full-screen exam
    └── results.html        # Exam results
```

## 🎨 Design System

### Colors
- **Primary**: #2563EB (Blue)
- **Success**: #10B981 (Green)
- **Error**: #EF4444 (Red)
- **Warning**: #F59E0B (Orange)
- **Purple**: #8B5CF6 (Accent)

### Typography
- **Font**: Inter, system-ui, sans-serif
- **Base**: 16px
- **Scale**: 12px - 48px

### Spacing
- **Base**: 4px
- **Scale**: 4px to 80px

## 📱 Platforms

### Web Application
| Page | Description |
|------|-------------|
| Landing | Marketing, hero, features, pricing |
| Auth | Login/register with tabs |
| Dashboard | Sidebar nav, stats, modules |
| MCQ Study | Questions, options, explanations |
| OSCE Practice | Patient scenarios, chat |
| OSCE Feedback | AI scoring, rubric breakdown |
| EMR | Cerner-style dark interface |
| Analytics | Charts, progress tracking |
| Bookmarks | Saved questions & notes |
| Study Plan | Schedule, checklist, AI coach |
| Settings | Account, notifications, billing |

### Mobile Application
- Bottom navigation (5 tabs)
- Full-screen MCQ with swipe
- Audio-first OSCE interface
- Touch-optimized EMR
- Floating action button

### Tablet Layout
- Collapsible sidebar
- 2-column master-detail
- Landscape optimized
- Touch-friendly

### Desktop App (Tauri)
- Native window frame
- Offline download manager
- Full-screen exam mode
- Keyboard shortcuts
- Results & analytics

## 📊 Dummy Data

### MCQs
- 18,000+ questions referenced
- Cardiology, Respiratory, Neurology
- Difficulty levels
- RAG citations
- Answer explanations

### OSCEs
- 3,000+ scenarios
- Patient profiles
- Vital signs
- Task lists
- AI chat simulation

### EMR
- 200+ patients
- Allergies, conditions
- SOAP notes
- Validation rules
- AI suggestions

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| 1-5 | Select answer |
| Space | Flag question |
| Enter | Submit |
| ←/→ | Navigate |
| Ctrl+M | MCQ |
| Ctrl+O | OSCE |
| Ctrl+E | EMR |
| Ctrl+Shift+E | Exam Mode |
| ? | Show help |
| Esc | Close modal |

## ✅ Features

- ✅ Design system with CSS variables
- ✅ Responsive for all screen sizes
- ✅ Interactive elements (hover, click)
- ✅ Realistic dummy data
- ✅ Touch targets (44px minimum)
- ✅ Keyboard shortcuts
- ✅ Dark mode (EMR)
- ✅ Mobile gestures indicated
- ✅ Offline mode indicators

## 📝 Specialties Covered

- Cardiology
- Respiratory
- Neurology
- Gastroenterology
- Endocrinology
- Nephrology
- Rheumatology
- Haematology
- Infectious Diseases
- Emergency Medicine
- Paediatrics
- Obstetrics
- Psychiatry
- Pharmacology

## 🎯 Modules

| Module | Web | Mobile | Tablet | Desktop |
|--------|-----|--------|--------|---------|
| Landing | ✅ | - | - | - |
| Auth | ✅ | - | - | - |
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| MCQ | ✅ | ✅ | - | ✅ |
| OSCE | ✅ | ✅ | - | - |
| EMR | ✅ | ✅ | - | - |
| Analytics | ✅ | - | - | - |
| Bookmarks | ✅ | - | - | - |
| Study Plan | ✅ | - | - | - |
| Settings | ✅ | - | - | - |
| Exam Mode | - | - | - | ✅ |

## 🛠️ Technical

- Pure HTML/CSS (no frameworks)
- Minimal JavaScript
- No external dependencies
- CSS custom properties
- Flexbox & Grid layouts
- Mobile-first responsive
- WCAG accessible colors

## 🔒 Exam Mode Features

- Full-screen interface
- System lockdown simulation
- Question navigator grid
- Flag for review
- Timer with warnings
- Keyboard navigation
- Submit confirmation
- Results breakdown

## 📧 Review Checklist

- [ ] Landing page professional
- [ ] Auth flow clear
- [ ] Dashboard informative
- [ ] MCQ interface usable
- [ ] OSCE scenarios clear
- [ ] EMR feels realistic
- [ ] Mobile nav intuitive
- [ ] Tablet optimized
- [ ] Desktop feels native
- [ ] Colors accessible
- [ ] Typography readable
- [ ] Touch targets adequate
- [ ] All interactions work
- [ ] Responsive at all sizes

---

**Note**: Static prototypes. Actual app uses React, FastAPI, PostgreSQL with real data, auth, and AI integration.
