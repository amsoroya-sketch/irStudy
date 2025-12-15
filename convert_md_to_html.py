#!/usr/bin/env python3
"""
ICRP Study Project - Markdown to HTML Converter
Converts all .md files to HTML with navigation and styling
"""

import os
import re
from pathlib import Path
from datetime import datetime

# HTML Template with Medical/Clinical Styling
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}

        /* Navigation Breadcrumbs */
        .breadcrumbs {{
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            margin: -40px -40px 30px -40px;
            border-radius: 8px 8px 0 0;
            font-size: 14px;
        }}

        .breadcrumbs a {{
            color: #3498db;
            text-decoration: none;
            margin-right: 5px;
        }}

        .breadcrumbs a:hover {{
            text-decoration: underline;
        }}

        .breadcrumbs span {{
            margin: 0 8px;
            color: #95a5a6;
        }}

        /* Quick Navigation */
        .quick-nav {{
            background: #ecf0f1;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}

        .quick-nav h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .quick-nav ul {{
            list-style: none;
        }}

        .quick-nav li {{
            margin: 8px 0;
        }}

        .quick-nav a {{
            color: #2980b9;
            text-decoration: none;
            padding: 5px 0;
            display: inline-block;
        }}

        .quick-nav a:hover {{
            color: #3498db;
            text-decoration: underline;
        }}

        /* Headers */
        h1 {{
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3498db;
            font-size: 2.5em;
        }}

        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #bdc3c7;
            font-size: 1.8em;
        }}

        h3 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}

        h4 {{
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 1.2em;
        }}

        /* Paragraphs and Lists */
        p {{
            margin-bottom: 15px;
            line-height: 1.8;
        }}

        ul, ol {{
            margin: 15px 0 15px 30px;
        }}

        li {{
            margin: 8px 0;
            line-height: 1.8;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}

        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}

        tr:hover {{
            background: #f5f5f5;
        }}

        /* Code Blocks */
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}

        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }}

        pre code {{
            background: none;
            color: #ecf0f1;
            padding: 0;
        }}

        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            color: #555;
            font-style: italic;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 4px;
        }}

        /* Medical Alert Boxes */
        .alert {{
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 5px solid;
        }}

        .alert-red {{
            background: #fee;
            border-color: #e74c3c;
            color: #c0392b;
        }}

        .alert-yellow {{
            background: #ffeaa7;
            border-color: #f39c12;
            color: #d68910;
        }}

        .alert-green {{
            background: #d5f4e6;
            border-color: #27ae60;
            color: #1e8449;
        }}

        .alert-blue {{
            background: #d6eaf8;
            border-color: #3498db;
            color: #21618c;
        }}

        /* Links */
        a {{
            color: #2980b9;
            text-decoration: none;
        }}

        a:hover {{
            color: #3498db;
            text-decoration: underline;
        }}

        /* Footer */
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}

        /* Checkboxes */
        input[type="checkbox"] {{
            margin-right: 8px;
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
            .breadcrumbs {{
                display: none;
            }}
            .quick-nav {{
                display: none;
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 2em;
            }}
            h2 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {breadcrumbs}
        {quick_nav}
        {content}
        {footer}
    </div>
</body>
</html>
"""

def convert_markdown_to_html(md_content):
    """Convert markdown content to HTML with enhanced formatting"""
    html = md_content

    # Headers (must be done in order from h6 to h1 to avoid nested replacements)
    html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and Italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

    # Code blocks (must be before inline code)
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    html = re.sub(r'^\*\*\*$', r'<hr>', html, flags=re.MULTILINE)

    # Blockquotes
    html = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists
    lines = html.split('\n')
    in_list = False
    result = []

    for line in lines:
        if re.match(r'^[\*\-]\s+', line):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item = re.sub(r'^[\*\-]\s+', '', line)
            result.append(f'<li>{item}</li>')
        elif re.match(r'^\d+\.\s+', line):
            if not in_list:
                result.append('<ol>')
                in_list = 'ordered'
            item = re.sub(r'^\d+\.\s+', '', line)
            result.append(f'<li>{item}</li>')
        else:
            if in_list == True:
                result.append('</ul>')
                in_list = False
            elif in_list == 'ordered':
                result.append('</ol>')
                in_list = False
            result.append(line)

    if in_list == True:
        result.append('</ul>')
    elif in_list == 'ordered':
        result.append('</ol>')

    html = '\n'.join(result)

    # Tables
    table_pattern = r'\|(.+)\|[\n\r]+\|[\s\-\:]+\|[\n\r]+((?:\|.+\|[\n\r]+)*)'

    def table_replacer(match):
        header = match.group(1)
        rows = match.group(2)

        # Process header
        headers = [h.strip() for h in header.split('|') if h.strip()]
        header_html = '<tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr>'

        # Process rows
        rows_html = ''
        for row in rows.strip().split('\n'):
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if cells:
                rows_html += '<tr>' + ''.join([f'<td>{c}</td>' for c in cells]) + '</tr>\n'

        return f'<table>\n<thead>\n{header_html}\n</thead>\n<tbody>\n{rows_html}</tbody>\n</table>'

    html = re.sub(table_pattern, table_replacer, html, flags=re.MULTILINE)

    # Checkboxes
    html = re.sub(r'\[ \]', r'<input type="checkbox">', html)
    html = re.sub(r'\[x\]', r'<input type="checkbox" checked>', html)
    html = re.sub(r'\[X\]', r'<input type="checkbox" checked>', html)

    # Paragraphs (wrap non-HTML lines)
    lines = html.split('\n')
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()
        if stripped and not re.match(r'^<[a-z]+', stripped):
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
        else:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)

    if in_paragraph:
        result.append('</p>')

    html = '\n'.join(result)

    # Highlight special medical content
    html = re.sub(r'RED FLAG', r'<span style="color: #e74c3c; font-weight: bold;">🚨 RED FLAG</span>', html, flags=re.IGNORECASE)
    html = re.sub(r'URGENT', r'<span style="color: #e74c3c; font-weight: bold;">URGENT</span>', html, flags=re.IGNORECASE)
    html = re.sub(r'EMERGENCY', r'<span style="color: #e74c3c; font-weight: bold;">⚠️ EMERGENCY</span>', html, flags=re.IGNORECASE)

    return html

def generate_breadcrumbs(file_path):
    """Generate breadcrumb navigation"""
    parts = Path(file_path).parts
    breadcrumbs = ['<div class="breadcrumbs">']
    breadcrumbs.append('<a href="/home/dev/Development/irStudy/MASTER_INDEX.html">🏠 Home</a>')

    current_path = ""
    for i, part in enumerate(parts[:-1]):  # Exclude filename
        if part in ['.', '..', 'home', 'dev', 'Development', 'irStudy']:
            continue
        current_path += part + "/"
        breadcrumbs.append('<span>→</span>')
        breadcrumbs.append(f'<span>{part.replace("_", " ")}</span>')

    breadcrumbs.append('</div>')
    return '\n'.join(breadcrumbs)

def generate_quick_nav(file_path):
    """Generate quick navigation based on file location"""
    path_obj = Path(file_path)
    parent_dir = path_obj.parent.name

    nav_links = {
        'Medicine': [
            ('MASTER_INDEX.html', 'Master Index'),
            ('01_Cardiovascular_Respiratory_History.html', 'CV/Resp History'),
            ('02_Physical_Examination_Cardiovascular_Respiratory.html', 'CV/Resp Exam'),
            ('03_Physical_Examination_Abdominal_Neurological.html', 'Abdo/Neuro Exam'),
        ],
        'Surgery': [
            ('01_Acute_Abdomen_History_Differentials.html', 'Acute Abdomen'),
            ('02_Acute_Abdomen_Physical_Examination.html', 'Abdo Exam'),
        ],
        'ObGyn': [
            ('01_Obstetric_History_Differentials.html', 'Obstetric History'),
            ('02_Gynaecological_History_Differentials.html', 'Gynae History'),
        ],
        'Paediatrics': [
            ('01_Paediatric_History_Differentials.html', 'Paeds History'),
            ('03_Paediatric_Physical_Examination.html', 'Paeds Exam'),
        ],
        'Psychiatry': [
            ('01_Psychiatric_History_Differentials.html', 'Psych History'),
            ('02_Mental_State_Examination.html', 'MSE'),
        ],
        'Ethics_Communication': [
            ('01_Communication_Skills_Role_Play_Scripts.html', 'Communication Skills'),
        ],
    }

    if parent_dir in nav_links:
        nav_html = ['<div class="quick-nav">']
        nav_html.append(f'<h3>📚 {parent_dir.replace("_", " ")} Navigation</h3>')
        nav_html.append('<ul>')
        for link, title in nav_links[parent_dir]:
            nav_html.append(f'<li><a href="{link}">{title}</a></li>')
        nav_html.append('</ul>')
        nav_html.append('</div>')
        return '\n'.join(nav_html)

    return ''

def generate_footer():
    """Generate footer with metadata"""
    return f'''
    <div class="footer">
        <p><strong>ICRP Study Project</strong> | NSW Young Hospital Preparation</p>
        <p>Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>
        <p><a href="/home/dev/Development/irStudy/MASTER_INDEX.html">Return to Master Index</a></p>
    </div>
    '''

def convert_file(md_file_path, base_dir):
    """Convert a single markdown file to HTML"""
    try:
        # Read markdown content
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else Path(md_file_path).stem.replace('_', ' ')

        # Convert markdown to HTML
        content_html = convert_markdown_to_html(md_content)

        # Generate navigation elements
        breadcrumbs = generate_breadcrumbs(md_file_path)
        quick_nav = generate_quick_nav(md_file_path)
        footer = generate_footer()

        # Create full HTML
        full_html = HTML_TEMPLATE.format(
            title=title,
            breadcrumbs=breadcrumbs,
            quick_nav=quick_nav,
            content=content_html,
            footer=footer
        )

        # Determine output path
        rel_path = os.path.relpath(md_file_path, base_dir)
        html_path = os.path.splitext(md_file_path)[0] + '.html'

        # Write HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        return True, html_path

    except Exception as e:
        return False, str(e)

def main():
    """Main conversion function"""
    base_dir = '/home/dev/Development/irStudy'
    os.chdir(base_dir)

    # Get all markdown files
    md_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    print(f"Found {len(md_files)} markdown files to convert\n")

    # Convert each file
    success_count = 0
    failed_files = []

    for md_file in sorted(md_files):
        rel_path = os.path.relpath(md_file, base_dir)
        print(f"Converting: {rel_path}")

        success, result = convert_file(md_file, base_dir)
        if success:
            success_count += 1
            print(f"  ✓ Created: {os.path.relpath(result, base_dir)}")
        else:
            failed_files.append((rel_path, result))
            print(f"  ✗ Failed: {result}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Conversion Complete!")
    print(f"{'='*60}")
    print(f"Total files: {len(md_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files:")
        for file, error in failed_files:
            print(f"  - {file}: {error}")

if __name__ == '__main__':
    main()
