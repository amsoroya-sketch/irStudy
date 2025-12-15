#!/usr/bin/env python3
"""
PDF Extraction Pipeline for Medical Textbooks
Extracts text from PDFs, handles OCR for scanned pages, preserves structure
"""

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
from pathlib import Path
import json
import logging
from typing import Dict, List
from tqdm import tqdm
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalPDFExtractor:
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_table(self, text: str) -> bool:
        """Detect if text contains table structure"""
        table_indicators = ['│', '┌', '┐', '└', '┘', '├', '┤', '─', '|']
        return any(indicator in text for indicator in table_indicators)

    def detect_drug_info(self, text: str) -> bool:
        """Detect if text contains drug dosage information"""
        patterns = [
            r'\d+\s*mg',
            r'\d+\s*mcg',
            r'\d+\s*g',
            r'\d+\s*mL',
            r'\d+\s*units',
            r'Dose:',
            r'Dosage:',
            r'Administration:',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    def extract_with_pymupdf(self, pdf_path: Path) -> Dict:
        """Extract text using PyMuPDF (fastest method)"""
        doc = fitz.open(pdf_path)

        book_data = {
            'filename': pdf_path.name,
            'source_path': str(pdf_path),
            'total_pages': len(doc),
            'pages': [],
            'metadata': {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
            },
            'has_images': False,
            'has_tables': False,
            'extraction_method': 'pymupdf'
        }

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text
            text = page.get_text("text")

            # Check if scanned (needs OCR)
            needs_ocr = len(text.strip()) < 50 and page.get_images()

            if needs_ocr:
                logger.info(f"  Page {page_num + 1} appears scanned, using OCR...")
                try:
                    # Render page as image
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # OCR
                    text = pytesseract.image_to_string(img)
                except Exception as e:
                    logger.warning(f"  OCR failed for page {page_num + 1}: {e}")
                    text = ""

            # Extract images
            images = page.get_images()

            # Detect special content
            has_table = self.detect_table(text)
            has_drug_info = self.detect_drug_info(text)

            page_data = {
                'page_number': page_num + 1,
                'text': text,
                'char_count': len(text),
                'word_count': len(text.split()),
                'images': len(images),
                'has_table': has_table,
                'has_drug_info': has_drug_info,
                'needs_special_handling': has_table or has_drug_info
            }

            book_data['pages'].append(page_data)

            if images:
                book_data['has_images'] = True
            if has_table:
                book_data['has_tables'] = True

        doc.close()
        return book_data

    def extract_tables_with_pdfplumber(self, pdf_path: Path) -> List[Dict]:
        """Extract tables using pdfplumber (more accurate for tables)"""
        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    for table_idx, table in enumerate(page_tables):
                        tables.append({
                            'page': page_num + 1,
                            'table_index': table_idx,
                            'data': table
                        })

        return tables

    def extract_pdf(self, pdf_path: Path) -> Dict:
        """Main extraction method"""
        logger.info(f"Extracting: {pdf_path.name}")

        # Primary extraction with PyMuPDF
        book_data = self.extract_with_pymupdf(pdf_path)

        # Enhanced table extraction if tables detected
        if book_data['has_tables']:
            logger.info(f"  Extracting tables with pdfplumber...")
            try:
                tables = self.extract_tables_with_pdfplumber(pdf_path)
                book_data['tables'] = tables
                logger.info(f"  Found {len(tables)} tables")
            except Exception as e:
                logger.warning(f"  Table extraction failed: {e}")
                book_data['tables'] = []

        # Statistics
        total_chars = sum(p['char_count'] for p in book_data['pages'])
        total_words = sum(p['word_count'] for p in book_data['pages'])

        book_data['statistics'] = {
            'total_characters': total_chars,
            'total_words': total_words,
            'avg_chars_per_page': total_chars / len(book_data['pages']) if book_data['pages'] else 0,
            'avg_words_per_page': total_words / len(book_data['pages']) if book_data['pages'] else 0,
        }

        logger.info(f"  ✓ Extracted {len(book_data['pages'])} pages, {total_words:,} words")

        return book_data

    def save_json(self, data: Dict, output_path: Path):
        """Save extracted data as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def process_all_pdfs(self, pdf_dir: str = "data/pdfs"):
        """Process all PDFs in directory"""
        pdf_path = Path(pdf_dir)

        if not pdf_path.exists():
            logger.error(f"PDF directory not found: {pdf_dir}")
            return

        # Find all PDFs
        pdf_files = list(pdf_path.rglob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        # Process each PDF
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            try:
                # Extract
                book_data = self.extract_pdf(pdf_file)

                # Save
                output_file = self.output_dir / f"{pdf_file.stem}.json"
                self.save_json(book_data, output_file)

            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue

        logger.info(f"\n✓ Processing complete! Output saved to {self.output_dir}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Extract text from medical PDF textbooks")
    parser.add_argument("--input", default="data/pdfs", help="Input directory containing PDFs")
    parser.add_argument("--output", default="data/processed", help="Output directory for JSON files")

    args = parser.parse_args()

    extractor = MedicalPDFExtractor(output_dir=args.output)
    extractor.process_all_pdfs(pdf_dir=args.input)


if __name__ == "__main__":
    main()
