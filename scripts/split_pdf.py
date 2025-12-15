#!/usr/bin/env python3
"""
PDF Splitter Script
Splits large PDF files into smaller parts based on number of pages or file count.

Usage:
    python split_pdf.py <input_pdf> [options]

Options:
    --pages N           Split every N pages (default: 50)
    --parts N           Split into N equal parts
    --output-dir DIR    Output directory (default: ./split_pdfs)
    --prefix PREFIX     Output file prefix (default: input filename)
"""

import sys
import os
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyPDF2
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependency: PyPDF2...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        print("✓ PyPDF2 installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install PyPDF2")
        print("Please run manually: pip install PyPDF2")
        return False

def split_pdf_by_pages(input_path, pages_per_split, output_dir, prefix):
    """Split PDF into chunks of specified page count."""
    from PyPDF2 import PdfReader, PdfWriter

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    print(f"Total pages: {total_pages}")
    print(f"Splitting every {pages_per_split} pages...")

    part_num = 1
    output_files = []

    for start_page in range(0, total_pages, pages_per_split):
        end_page = min(start_page + pages_per_split, total_pages)

        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        output_filename = f"{prefix}_part{part_num:03d}_pages{start_page+1}-{end_page}.pdf"
        output_path = output_dir / output_filename

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✓ Created: {output_filename} ({file_size:.2f} MB, pages {start_page+1}-{end_page})")
        output_files.append(output_path)
        part_num += 1

    return output_files

def split_pdf_by_parts(input_path, num_parts, output_dir, prefix):
    """Split PDF into specified number of equal parts."""
    from PyPDF2 import PdfReader, PdfWriter

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    pages_per_part = total_pages // num_parts
    remainder = total_pages % num_parts

    print(f"Total pages: {total_pages}")
    print(f"Splitting into {num_parts} parts (~{pages_per_part} pages each)...")

    output_files = []
    current_page = 0

    for part_num in range(1, num_parts + 1):
        # Distribute remainder pages across first parts
        pages_in_this_part = pages_per_part + (1 if part_num <= remainder else 0)

        writer = PdfWriter()
        for _ in range(pages_in_this_part):
            if current_page < total_pages:
                writer.add_page(reader.pages[current_page])
                current_page += 1

        start_page = current_page - pages_in_this_part + 1
        end_page = current_page

        output_filename = f"{prefix}_part{part_num:03d}_pages{start_page}-{end_page}.pdf"
        output_path = output_dir / output_filename

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✓ Created: {output_filename} ({file_size:.2f} MB, pages {start_page}-{end_page})")
        output_files.append(output_path)

    return output_files

def main():
    parser = argparse.ArgumentParser(
        description='Split large PDF files into smaller parts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split every 50 pages (default)
  python split_pdf.py large_book.pdf

  # Split every 100 pages
  python split_pdf.py large_book.pdf --pages 100

  # Split into 5 equal parts
  python split_pdf.py large_book.pdf --parts 5

  # Custom output directory and prefix
  python split_pdf.py large_book.pdf --output-dir ./output --prefix mybook
        """
    )

    parser.add_argument('input_pdf', nargs='?', help='Input PDF file path')
    parser.add_argument('--pages', type=int, help='Split every N pages')
    parser.add_argument('--parts', type=int, help='Split into N equal parts')
    parser.add_argument('--output-dir', help='Output directory (default: ./split_pdfs)')
    parser.add_argument('--prefix', help='Output file prefix (default: input filename)')
    parser.add_argument('--install', action='store_true', help='Install required dependencies')

    args = parser.parse_args()

    # Handle dependency installation
    if args.install:
        if install_dependencies():
            print("\nDependencies installed. You can now use the script normally.")
        sys.exit(0)

    # Validate input_pdf is provided for normal operation
    if not args.input_pdf:
        parser.error("input_pdf is required unless using --install")

    # Check dependencies
    if not check_dependencies():
        print("✗ Missing required dependency: PyPDF2")
        print("\nTo install, run:")
        print(f"  python {sys.argv[0]} --install")
        print("OR manually:")
        print("  pip install PyPDF2")
        sys.exit(1)

    # Validate input file
    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"✗ Error: Input file not found: {input_path}")
        sys.exit(1)

    if not input_path.suffix.lower() == '.pdf':
        print(f"✗ Error: Input file must be a PDF: {input_path}")
        sys.exit(1)

    # Set up output directory
    output_dir = Path(args.output_dir) if args.output_dir else Path('./split_pdfs')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up prefix
    prefix = args.prefix if args.prefix else input_path.stem

    # Determine split mode
    if args.parts and args.pages:
        print("✗ Error: Cannot specify both --pages and --parts")
        sys.exit(1)

    try:
        input_size = input_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\nInput file: {input_path.name} ({input_size:.2f} MB)")
        print(f"Output directory: {output_dir}\n")

        if args.parts:
            output_files = split_pdf_by_parts(input_path, args.parts, output_dir, prefix)
        else:
            pages_per_split = args.pages if args.pages else 50
            output_files = split_pdf_by_pages(input_path, pages_per_split, output_dir, prefix)

        print(f"\n✓ Successfully created {len(output_files)} files in {output_dir}")

    except Exception as e:
        print(f"\n✗ Error during PDF splitting: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
