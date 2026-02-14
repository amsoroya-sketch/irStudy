# Respiratory MCQ App - Deployment Guide

## Files
- `index.html` - Production build (single file, all resources inlined)

## Deployment Options

### Option 1: Static Hosting (Recommended)
Deploy to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Any web server

### Option 2: Local File
Simply open `index.html` in a web browser.
No server required - works completely offline.

### Option 3: Python HTTP Server (Development/Testing)
```bash
python3 -m http.server 8000
# Access at http://localhost:8000
```

## Features
- ✅ 200 Week 3 Respiratory MCQs
- ✅ Australian medical context
- ✅ Copy protection enabled
- ✅ Code obfuscation applied
- ✅ Progress tracking (LocalStorage)
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Offline capable

## Security Features
- Right-click disabled
- Copy/paste prevention
- DevTools detection
- Code minification & obfuscation
- Print prevention

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Android)

## Size
- Single HTML file: ~1274 KB
- Gzipped: ~425 KB (estimated)

Built: 2026-01-31T03:51:47.234Z
