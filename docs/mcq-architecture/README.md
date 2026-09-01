# MCQ Page Architecture Documentation

**Location:** `/home/dev/Development/irStudy/docs/mcq-architecture/`

## 📖 Overview

This directory contains split, interactive HTML documentation for the MCQ browser page (`http://localhost:5173/mcqs`). The documentation is organized into logical sections for easy navigation and understanding.

## 🗂️ File Structure

```
mcq-architecture/
├── README.md                          # This file
├── index.html                         # Navigation hub (START HERE)
├── 01-overview.html                   # Architecture & technology stack
├── 02-request-flow.html              # Request flow analysis
├── 03-frontend-components.html       # React components with code
├── 04-api-layer.html                 # API client & Axios
├── 05-backend-api.html               # FastAPI endpoints
├── 06-issues-troubleshooting.html    # Debugging guide
└── styles.css                         # Shared stylesheet
```

## 🚀 Quick Start

### Open in Browser

```bash
# From project root
cd /home/dev/Development/irStudy/docs/mcq-architecture

# Open index page in browser
xdg-open index.html

# Or use Firefox/Chrome directly
firefox index.html
google-chrome index.html
```

### Start Web Server (Recommended)

For better experience with cross-origin requests:

```bash
# Option 1: Python HTTP server
cd /home/dev/Development/irStudy/docs/mcq-architecture
python3 -m http.server 8080
# Then open: http://localhost:8080

# Option 2: Node.js http-server (if installed)
npx http-server -p 8080

# Option 3: Use VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

## 📚 How to Navigate

### For New Developers (Read in Order)

1. **index.html** - Start here for overview and navigation
2. **01-overview.html** - Understand the technology stack and architecture
3. **02-request-flow.html** - Learn how data flows through the system
4. **03-frontend-components.html** - Study React component implementation
5. **04-api-layer.html** - Explore HTTP client and authentication
6. **05-backend-api.html** - Understand server-side endpoints
7. **06-issues-troubleshooting.html** - Reference for debugging

### For Debugging

1. Go directly to **06-issues-troubleshooting.html**
2. Find your error symptoms
3. Follow step-by-step resolution guides
4. Use browser DevTools commands provided in examples

### For Code Review

1. **03-frontend-components.html** - Frontend code review
2. **04-api-layer.html** - API client review
3. **05-backend-api.html** - Backend endpoint review

## 🎯 What's Inside Each Section

### 01 - Overview
- Complete technology stack
- Development environment setup
- Project structure
- 7-layer architecture diagram
- Design patterns used

### 02 - Request Flow
- Step-by-step user → server → database flow
- Component interactions
- Authentication checkpoints
- Data transformation at each layer

### 03 - Frontend Components
- App.tsx source code and explanation
- MCQBrowser.tsx implementation
- React Query integration
- State management patterns
- UI component hierarchy

### 04 - API Layer
- Axios instance configuration
- Request/Response interceptors
- Authentication header injection
- Token refresh mechanism
- Error handling strategies

### 05 - Backend API
- FastAPI endpoint definitions
- JWT validation dependencies
- Database query patterns
- Response schemas
- Australian medical content standards

### 06 - Issues & Troubleshooting
- **Primary Issue:** Authentication failure (401 Unauthorized)
- Root cause analysis
- Step-by-step resolution
- Common problems and solutions
- Debugging commands and tools

## 🔍 Code Examples Included

Each section contains:

- **Syntax-highlighted code blocks** with line-by-line explanations
- **Actual source code** from the project files
- **Interactive examples** (where applicable)
- **Copy buttons** for easy code reuse
- **File locations** for reference

## 📊 Visual Aids

- **Architecture diagram** (PNG, 300 DPI, 1.1 MB)
- **Flow charts** showing request/response cycles
- **Component hierarchy** visualizations
- **Color-coded** layers and error states

## 🎨 Features

### Interactive Elements

- **Hover effects** on component cards
- **Clickable navigation** between sections
- **Expandable code blocks** with syntax highlighting
- **Breadcrumb navigation** on each page

### Code Blocks

- **Syntax highlighting** for TypeScript, Python, SQL
- **Copy buttons** for code snippets
- **File headers** showing source location
- **Comments** explaining key lines

### Responsive Design

- Works on desktop and mobile
- Readable on different screen sizes
- Print-friendly CSS

## 🔗 Related Files

In parent directory (`/home/dev/Development/irStudy/docs/`):

- **mcq_architecture_diagram.png** - Visual architecture diagram
- **MCQ_PAGE_DIAGNOSIS_REPORT.md** - Complete technical report (961 lines)
- **mcq_architecture_analysis.pdf** - PDF version
- **mcq_architecture_analysis.html** - Single-page version (original)

## 💡 Tips for Exploration

### Search Functionality

Use browser's Find feature (Ctrl+F / Cmd+F) to search within pages:
- Search for error messages
- Find specific function names
- Locate API endpoints

### Browser DevTools

Use while viewing docs to:
- Inspect CSS styling
- Modify colors/fonts for preference
- Test JavaScript interactions

### Linking to Specific Sections

Each page has anchor links. Share specific sections:
```
file:///home/dev/Development/irStudy/docs/mcq-architecture/03-frontend-components.html#app-component
```

## 🛠️ Customization

### Modify Styles

Edit `styles.css` to change:
- Color scheme (currently purple/blue gradient)
- Font sizes
- Component spacing
- Code block themes

### Add New Sections

Follow the existing pattern:
1. Copy an existing HTML file
2. Update breadcrumb navigation
3. Add content in `<div class="section">` blocks
4. Link from `index.html`

## 📝 Maintenance

### Updating Content

When code changes:
1. Update relevant section HTML
2. Re-read source files if needed
3. Test all navigation links
4. Regenerate PDF if needed

### Regenerating PDF

```bash
# Using Chrome headless
google-chrome --headless --disable-gpu --print-to-pdf=docs.pdf index.html

# Or combine all sections
cat 0*.html > full-docs.html
google-chrome --headless --disable-gpu --print-to-pdf=full-docs.pdf full-docs.html
```

## 🐛 Troubleshooting Docs Viewing

### Issue: Styles Not Loading

**Cause:** Relative path issues  
**Solution:** Open `index.html` directly or use web server

### Issue: Images Not Showing

**Cause:** Relative paths to parent directory  
**Solution:** Ensure `../mcq_architecture_diagram.png` exists

### Issue: Navigation Links 404

**Cause:** Files not in same directory  
**Solution:** Verify all HTML files in `mcq-architecture/` folder

## 📞 Support

For questions about:
- **Documentation content:** Refer to `MCQ_PAGE_DIAGNOSIS_REPORT.md`
- **Actual code issues:** Check `06-issues-troubleshooting.html`
- **Architecture questions:** Read `01-overview.html` and `02-request-flow.html`

## 🎓 Learning Path

**Beginner** (2-3 hours):
1. Read 01-overview
2. Skim 02-request-flow
3. Bookmark 06-troubleshooting

**Intermediate** (4-6 hours):
1. Deep dive all sections in order
2. Compare code examples with actual files
3. Test API endpoints with curl

**Advanced** (Full day):
1. Read all documentation
2. Trace code flow in VSCode
3. Debug live application
4. Modify and test changes

---

**Documentation Generated:** May 26, 2026  
**Format:** HTML + CSS  
**Total Size:** ~150 KB (excluding images)  
**Browser Support:** All modern browsers (Chrome, Firefox, Safari, Edge)
