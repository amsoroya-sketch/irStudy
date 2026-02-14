# Week 3 Respiratory Medicine MCQs - Web Application

A lightweight, secure, and responsive web application for studying 200 Australian medical context MCQs.

## ✨ Features

### 📚 Content
- **200 MCQs**: Complete Week 3 Respiratory Medicine curriculum
- **Australian Context**: All content uses Australian medical guidelines (eTG, TSANZ, ANZICS, Cancer Council)
- **Comprehensive Explanations**: Detailed explanations with citations
- **Learning Objectives**: Key learning points for each MCQ

### 🎯 Functionality
- ✅ **Answer Checking**: Immediate feedback on correct/incorrect answers
- ✅ **Progress Tracking**: Automatic saving with LocalStorage
- ✅ **Topic Filtering**: Filter by respiratory topics (Asthma, COPD, Pneumonia, etc.)
- ✅ **View Modes**: All questions, Unanswered, Incorrect only, Flagged for review
- ✅ **Navigation**: Next/Previous buttons, Jump to specific question, Keyboard shortcuts
- ✅ **Statistics**: Real-time score percentage, answered count, correct count

### 🔒 Security Features
- **Copy Protection**: Disabled text selection, right-click, and copy shortcuts
- **Code Obfuscation**: Minified and obfuscated JavaScript
- **DevTools Detection**: Detects and warns when developer tools are open
- **Print Prevention**: Printing is disabled
- **Anti-Debugging**: Basic anti-debugging measures

### 📱 Responsive Design
- **Mobile-First**: Optimized for mobile devices (320px+)
- **Tablet Support**: Enhanced layout for tablets (768px+)
- **Desktop Support**: Full-featured desktop experience (1024px+)
- **Touch-Friendly**: Large tap targets (44x44px minimum)

### ⚡ Performance
- **Lightweight**: ~1.3MB total (includes 200 MCQs)
- **Fast Loading**: Vanilla JavaScript, no framework overhead
- **Offline Capable**: Works without internet after initial load
- **No Dependencies**: Zero external libraries in production build

---

## 🚀 Quick Start

### Option 1: Use Development Version (With Hot Reload)

```bash
cd respiratory-mcq-app

# Serve development files
npm run serve:dev
# OR
python3 -m http.server 8000 --directory src

# Access at http://localhost:8000
```

### Option 2: Build and Deploy Production Version

```bash
cd respiratory-mcq-app

# Install build dependencies (first time only)
npm install

# Build production version
npm run build

# Serve production build
npm run serve:prod
# OR
python3 -m http.server 8000 --directory build

# Access at http://localhost:8000
```

### Option 3: Open Directly (No Server)

Simply open `build/index.html` in any web browser. No server required!

---

## 📁 Project Structure

```
respiratory-mcq-app/
├── src/                    # Source files (development)
│   ├── index.html          # Main HTML structure
│   ├── styles.css          # CSS (mobile-first, responsive)
│   └── app.js              # JavaScript application logic
│
├── build/                  # Production build (generated)
│   ├── index.html          # Single-file production build
│   └── README.md           # Deployment guide
│
├── data/                   # MCQ data
│   └── mcqs.json           # 200 MCQs (copied from main project)
│
├── build.js                # Build script (minification + obfuscation)
├── package.json            # npm configuration & scripts
└── README.md               # This file
```

---

## 🛠️ Development

### Prerequisites
- Node.js 14+ (for build script only)
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)

### Development Workflow

1. **Make changes** to files in `src/` directory
2. **Test locally** using development server:
   ```bash
   npm run serve:dev
   ```
3. **Build production** version:
   ```bash
   npm run build
   ```
4. **Test production** build:
   ```bash
   npm run serve:prod
   ```

### File Descriptions

#### `src/index.html`
- Semantic HTML5 structure
- Accessibility features (ARIA labels, keyboard navigation)
- Mobile-responsive meta tags

#### `src/styles.css`
- CSS Custom Properties (variables) for theming
- Mobile-first responsive design
- Copy protection styles (user-select: none)
- Print prevention

#### `src/app.js`
- Vanilla JavaScript (ES6+)
- State management with closure pattern
- LocalStorage for progress persistence
- Security features (right-click prevention, DevTools detection)

#### `build.js`
- Minifies CSS (31% reduction)
- Minifies JavaScript (40% reduction)
- Obfuscates MCQ data (Base64 encoding + chunking)
- Inlines all resources into single HTML file
- Adds anti-debugging code

---

## 📊 Build Statistics

- **Original source**: ~47 KB (HTML + CSS + JS)
- **MCQ data**: ~1.2 MB (200 MCQs with full content)
- **Production build**: ~1.3 MB (single HTML file)
- **Estimated gzipped**: ~430 KB

### What Gets Optimized?
- ✅ CSS minification (31% reduction)
- ✅ JavaScript minification (40% reduction)
- ✅ MCQ data obfuscation (Base64 + chunking)
- ✅ All resources inlined (no HTTP requests)

---

## 🔐 Security Features Explained

### Copy Protection
**Purpose**: Prevent casual copying of MCQ content

**Methods**:
- CSS `user-select: none` on all non-input elements
- JavaScript event prevention (`contextmenu`, `selectstart`, `dragstart`)
- Keyboard shortcut blocking (Ctrl+C, Ctrl+U, Ctrl+S, F12, etc.)

**Limitations**:
- Screenshots can still capture content
- Technical users can bypass with browser DevTools
- Goal is to prevent casual copying, not 100% prevention

### Code Obfuscation
**Purpose**: Make source code harder to read and extract data

**Methods**:
- Variable name mangling (basic)
- MCQ data Base64 encoding + chunking
- Anti-debugging code injection
- Minification (whitespace removal)

**Limitations**:
- Not true encryption - can be deobfuscated with tools
- Goal is to increase effort required, not make impossible

### DevTools Detection
**Purpose**: Detect when developer tools are open

**Method**:
- Monitor window dimensions (DevTools increases size)
- Console warnings when detected

**Limitations**:
- Can be bypassed with detached DevTools window
- Not foolproof, but adds deterrent

---

## 🎨 Customization

### Changing Colors
Edit CSS variables in `src/styles.css`:

```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #27ae60;
    --danger-color: #e74c3c;
    /* ... */
}
```

### Changing Content
Replace `data/mcqs.json` with your own MCQ data following this structure:

```json
{
  "metadata": { ... },
  "statistics": { ... },
  "mcqs": [
    {
      "id": "WEEK3-RESP-001",
      "question": {
        "scenario": "Clinical scenario...",
        "stem": "Question stem...",
        "options": {
          "A": "Option A",
          "B": "Option B",
          "C": "Option C",
          "D": "Option D"
        }
      },
      "correct_answer": "C",
      "explanation": "Detailed explanation...",
      "summary": "Key summary...",
      "citations": ["Source 1", "Source 2"],
      "topic": "Topic name",
      "learning_objectives": ["Objective 1", "Objective 2"]
    }
  ]
}
```

---

## 🌐 Deployment Options

### Option 1: Static Hosting (Recommended)

**GitHub Pages**:
```bash
# Commit build/index.html to repository
git add build/index.html
git commit -m "Add production build"
git push

# Enable GitHub Pages in repository settings
# Select branch and /build folder
```

**Netlify**:
1. Drag and drop `build/` folder to Netlify
2. Or connect GitHub repo with build command: `npm run build`

**Vercel**:
```bash
vercel --prod build/
```

### Option 2: Self-Hosted
Upload `build/index.html` to any web server (Apache, Nginx, etc.)

### Option 3: Local Distribution
Share `build/index.html` file directly. Users can open it in any browser.

---

## 🧪 Testing Checklist

### Functional Testing
- [ ] All 200 MCQs load correctly
- [ ] Answer selection works
- [ ] Submit answer provides correct feedback
- [ ] Explanations display with citations
- [ ] Progress saves to LocalStorage
- [ ] Progress persists after page reload
- [ ] Navigation (next/prev/jump) works
- [ ] Topic filtering works
- [ ] View modes (unanswered/incorrect/flagged) work
- [ ] Flag/unflag functionality works
- [ ] Statistics update correctly
- [ ] Reset progress works

### Security Testing
- [ ] Right-click disabled
- [ ] Ctrl+C/Cmd+C disabled
- [ ] Ctrl+U/Cmd+U disabled (view source)
- [ ] F12 disabled
- [ ] Text selection disabled
- [ ] Drag & drop disabled
- [ ] DevTools detection works
- [ ] Source code is obfuscated
- [ ] MCQ data is obfuscated

### Responsive Testing
- [ ] Works on mobile (320px - 767px)
- [ ] Works on tablet (768px - 1023px)
- [ ] Works on desktop (1024px+)
- [ ] Touch gestures work on mobile
- [ ] Buttons are tap-friendly (44x44px min)
- [ ] Text is readable on all devices

### Browser Testing
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+
- [ ] iOS Safari
- [ ] Chrome Android

### Performance Testing
- [ ] Page loads in <2 seconds (3G connection)
- [ ] No layout shifts during load
- [ ] Smooth scrolling and animations
- [ ] LocalStorage saves without lag

---

## 🐛 Troubleshooting

### MCQs Not Loading
**Problem**: Blank screen or "Failed to load MCQs" error

**Solutions**:
1. Check browser console for errors (F12)
2. Ensure `data/mcqs.json` exists and is valid JSON
3. For development server, ensure you're serving from correct directory
4. Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Progress Not Saving
**Problem**: Progress resets after page reload

**Solutions**:
1. Check if LocalStorage is enabled in browser
2. Check browser console for storage errors
3. Clear browser cache and try again
4. Ensure not in Private/Incognito mode (LocalStorage disabled)

### Copy Protection Not Working
**Problem**: Users can still copy content

**Solutions**:
1. Ensure production build is being used (not development version)
2. Check that JavaScript is enabled
3. Note: Screenshots will always work - this is expected
4. Some browser extensions can bypass protection

### Build Script Fails
**Problem**: `npm run build` throws errors

**Solutions**:
1. Run `npm install` first to install dependencies
2. Ensure Node.js 14+ is installed
3. Check file permissions on build.js
4. Verify source files exist in `src/` directory

---

## 📝 License

**UNLICENSED** - Private educational use only.

This application contains proprietary medical education content. Distribution requires permission.

---

## 🙏 Acknowledgments

- **MCQ Content**: Week 3 Respiratory Medicine curriculum
- **Australian Guidelines**: eTG Complete, TSANZ, ANZICS, Cancer Council Australia
- **Design Inspiration**: Modern medical education platforms
- **Security Techniques**: Various web security best practices

---

## 📧 Support

For issues or questions, please contact the project administrator.

---

**Built with**: Vanilla JavaScript, HTML5, CSS3
**Build Date**: ${new Date().toISOString()}
**Version**: 1.0.0
