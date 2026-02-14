#!/usr/bin/env node
/**
 * Build Script for Respiratory MCQ App
 * - Minifies CSS and JavaScript
 * - Obfuscates MCQ data
 * - Inlines all resources into single HTML file
 * - Adds additional security measures
 */

const fs = require('fs');
const path = require('path');

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    srcDir: path.join(__dirname, 'src'),
    buildDir: path.join(__dirname, 'build'),
    dataDir: path.join(__dirname, 'data'),
    files: {
        html: 'index.html',
        css: 'styles.css',
        js: 'app.js',
        mcqData: 'mcqs.json'
    }
};

// ============================================
// SIMPLE MINIFICATION (No external dependencies)
// ============================================
function minifyCSS(css) {
    return css
        // Remove comments
        .replace(/\/\*[\s\S]*?\*\//g, '')
        // Remove whitespace
        .replace(/\s+/g, ' ')
        // Remove spaces around special characters
        .replace(/\s*([{}:;,>+~])\s*/g, '$1')
        // Remove last semicolon
        .replace(/;}/g, '}')
        .trim();
}

function minifyJS(js) {
    return js
        // Remove single-line comments (but preserve URLs)
        .replace(/\/\/(?![^\n]*:\/\/)[^\n]*/g, '')
        // Remove multi-line comments
        .replace(/\/\*[\s\S]*?\*\//g, '')
        // Remove unnecessary whitespace (basic minification)
        .replace(/\s+/g, ' ')
        .replace(/\s*([{}();,:])\s*/g, '$1')
        .trim();
}

// ============================================
// DATA OBFUSCATION
// ============================================
function obfuscateMCQData(mcqs) {
    // Convert to JSON string
    const jsonString = JSON.stringify(mcqs);

    // Base64 encode
    const base64 = Buffer.from(jsonString).toString('base64');

    // Split into chunks to make it harder to extract
    const chunkSize = 1000;
    const chunks = [];
    for (let i = 0; i < base64.length; i += chunkSize) {
        chunks.push(base64.slice(i, i + chunkSize));
    }

    // Generate obfuscated loader code
    const loaderCode = `
(function() {
    const _0x1a2b = ${JSON.stringify(chunks)};
    const _0x3c4d = _0x1a2b.join('');
    const _0x5e6f = atob(_0x3c4d);
    const _0x7g8h = JSON.parse(_0x5e6f);
    window.__MCQ_DATA__ = _0x7g8h;
})();
    `.trim();

    return loaderCode;
}

// ============================================
// BUILD PROCESS
// ============================================
function build() {
    console.log('🔨 Building Respiratory MCQ App...\n');

    // Create build directory if it doesn't exist
    if (!fs.existsSync(CONFIG.buildDir)) {
        fs.mkdirSync(CONFIG.buildDir, { recursive: true });
        console.log('✓ Created build directory');
    }

    // 1. Read source files
    console.log('📖 Reading source files...');
    const htmlContent = fs.readFileSync(path.join(CONFIG.srcDir, CONFIG.files.html), 'utf8');
    const cssContent = fs.readFileSync(path.join(CONFIG.srcDir, CONFIG.files.css), 'utf8');
    const jsContent = fs.readFileSync(path.join(CONFIG.srcDir, CONFIG.files.js), 'utf8');
    const mcqData = JSON.parse(fs.readFileSync(path.join(CONFIG.dataDir, CONFIG.files.mcqData), 'utf8'));
    console.log('✓ Source files loaded\n');

    // 2. Minify CSS
    console.log('🎨 Minifying CSS...');
    const minifiedCSS = minifyCSS(cssContent);
    console.log(`✓ CSS minified: ${cssContent.length} → ${minifiedCSS.length} bytes (${Math.round((1 - minifiedCSS.length / cssContent.length) * 100)}% reduction)\n`);

    // 3. Obfuscate MCQ data
    console.log('🔒 Obfuscating MCQ data...');
    const obfuscatedData = obfuscateMCQData(mcqData.mcqs);
    console.log(`✓ MCQ data obfuscated (${mcqData.mcqs.length} MCQs)\n`);

    // 4. Modify JavaScript to use obfuscated data
    console.log('⚙️ Processing JavaScript...');
    let modifiedJS = jsContent.replace(
        'await fetch(\'../data/mcqs.json\')',
        'Promise.resolve({ ok: true, json: () => Promise.resolve({ mcqs: window.__MCQ_DATA__ }) })'
    );

    // Add anti-debugging code
    const antiDebuggingCode = `
(function() {
    const _0x9i0j = function() {
        const _0x1k2l = function() { return true; };
        const _0x3m4n = function() { debugger; };
        return (function() { _0x3m4n(); })['constructor']('while(true){}')['apply']('counter');
    };
    try { _0x9i0j(); } catch(e) {}
    setInterval(function() {
        (function() { return false; })['constructor']('debugger')['call']('action');
    }, 4000);
})();
    `.trim();

    // 5. Minify JavaScript
    const minifiedJS = minifyJS(modifiedJS);
    console.log(`✓ JavaScript processed: ${jsContent.length} → ${minifiedJS.length} bytes (${Math.round((1 - minifiedJS.length / jsContent.length) * 100)}% reduction)\n`);

    // 6. Combine everything into single HTML
    console.log('📦 Creating production build...');
    let finalHTML = htmlContent
        // Inline CSS
        .replace('<link rel="stylesheet" href="styles.css">', `<style>${minifiedCSS}</style>`)
        // Inline obfuscated data + anti-debugging + app JS
        .replace('<script src="app.js"></script>', `<script>${obfuscatedData}\n${antiDebuggingCode}\n${minifiedJS}</script>`)
        // Add additional meta tags for security
        .replace('</head>', `
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="referrer" content="no-referrer">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
</head>`);

    // 7. Write production build
    const outputPath = path.join(CONFIG.buildDir, 'index.html');
    fs.writeFileSync(outputPath, finalHTML, 'utf8');
    console.log(`✓ Production build created: ${outputPath}\n`);

    // 8. Calculate final size
    const finalSize = fs.statSync(outputPath).size;
    const totalOriginalSize = htmlContent.length + cssContent.length + jsContent.length;
    console.log('📊 Build Statistics:');
    console.log(`   Original size: ${Math.round(totalOriginalSize / 1024)} KB`);
    console.log(`   Final size: ${Math.round(finalSize / 1024)} KB`);
    console.log(`   Compression: ${Math.round((1 - finalSize / totalOriginalSize) * 100)}%`);

    // 9. Create README for deployment
    const readmeContent = `# Respiratory MCQ App - Deployment Guide

## Files
- \`index.html\` - Production build (single file, all resources inlined)

## Deployment Options

### Option 1: Static Hosting (Recommended)
Deploy to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Any web server

### Option 2: Local File
Simply open \`index.html\` in a web browser.
No server required - works completely offline.

### Option 3: Python HTTP Server (Development/Testing)
\`\`\`bash
python3 -m http.server 8000
# Access at http://localhost:8000
\`\`\`

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
- Single HTML file: ~${Math.round(finalSize / 1024)} KB
- Gzipped: ~${Math.round(finalSize / 1024 / 3)} KB (estimated)

Built: ${new Date().toISOString()}
`;

    fs.writeFileSync(path.join(CONFIG.buildDir, 'README.md'), readmeContent, 'utf8');
    console.log('\n✅ Build complete! Check the build/ directory.\n');
}

// ============================================
// RUN BUILD
// ============================================
try {
    build();
} catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
}
