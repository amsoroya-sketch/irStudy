#!/usr/bin/env python3
"""
File Integrity Manager for Medical Resources Download System

Implements industry-standard file integrity verification using:
- SHA-256 checksums (NIST FIPS 180-4 compliant)
- BagIt file packaging format (RFC 8493)
- Automated corruption detection
- File provenance tracking

Security Features:
- Cryptographic hash verification
- Corruption detection for PDFs, XMLs, JSON
- Quarantine system for invalid files
- Manifest-based integrity auditing

Usage:
    from scripts.lib.file_integrity import FileIntegrityManager

    integrity_mgr = FileIntegrityManager()

    # Calculate and store checksum
    checksum = integrity_mgr.calculate_checksum(file_path)

    # Validate file integrity
    is_valid = integrity_mgr.validate_file(file_path, expected_checksum)

    # Create BagIt package for resource
    bag = integrity_mgr.create_bag(resource_dir)
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import logging

# Optional: BagIt support
try:
    import bagit
    BAGIT_AVAILABLE = True
except ImportError:
    BAGIT_AVAILABLE = False
    logging.warning("bagit library not installed. Install with: pip install bagit")

# Optional: PDF validation
try:
    from PyPDF2 import PdfReader
    PDF_VALIDATION_AVAILABLE = True
except ImportError:
    PDF_VALIDATION_AVAILABLE = False
    logging.warning("PyPDF2 not installed. Install with: pip install PyPDF2")

# Optional: XML validation
try:
    from lxml import etree
    XML_VALIDATION_AVAILABLE = True
except ImportError:
    XML_VALIDATION_AVAILABLE = False
    logging.warning("lxml not installed. Install with: pip install lxml")

logger = logging.getLogger(__name__)


class FileIntegrityManager:
    """Manages file integrity verification and BagIt packaging"""

    SUPPORTED_ALGORITHMS = ['md5', 'sha256', 'sha512']

    def __init__(self, quarantine_dir: Optional[Path] = None):
        """
        Initialize FileIntegrityManager

        Args:
            quarantine_dir: Directory to store quarantined files
                           Defaults to /mnt/data/medical_resources/.quarantine
        """
        if quarantine_dir is None:
            quarantine_dir = Path('/mnt/data/medical_resources/.quarantine')

        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def calculate_checksum(self,
                          filepath: Path,
                          algorithm: str = 'sha256',
                          chunk_size: int = 65536) -> str:
        """
        Calculate cryptographic hash of file

        Args:
            filepath: Path to file
            algorithm: Hash algorithm ('md5', 'sha256', 'sha512')
            chunk_size: Read buffer size (default 64KB)

        Returns:
            Hexadecimal hash string

        Raises:
            ValueError: If algorithm not supported
            FileNotFoundError: If file doesn't exist
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. "
                           f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS)}")

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Initialize hash object
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha512':
            hasher = hashlib.sha512()

        # Read and hash file in chunks
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        checksum = hasher.hexdigest()
        logger.debug(f"Calculated {algorithm} checksum for {filepath.name}: {checksum}")
        return checksum

    def validate_file(self,
                     filepath: Path,
                     expected_checksum: str,
                     algorithm: str = 'sha256') -> Dict[str, any]:
        """
        Validate file integrity against expected checksum

        Args:
            filepath: Path to file
            expected_checksum: Expected hash value
            algorithm: Hash algorithm used

        Returns:
            dict: Validation result with keys:
                - valid (bool): True if checksum matches
                - actual_checksum (str): Calculated checksum
                - expected_checksum (str): Expected checksum
                - size_bytes (int): File size
                - errors (list): List of error messages
        """
        result = {
            'valid': True,
            'actual_checksum': None,
            'expected_checksum': expected_checksum,
            'size_bytes': 0,
            'errors': []
        }

        # Check file exists
        if not filepath.exists():
            result['valid'] = False
            result['errors'].append(f"File does not exist: {filepath}")
            return result

        # Get file size
        result['size_bytes'] = filepath.stat().st_size

        # Check file not empty
        if result['size_bytes'] == 0:
            result['valid'] = False
            result['errors'].append("File is empty (0 bytes)")
            return result

        # Calculate checksum
        try:
            result['actual_checksum'] = self.calculate_checksum(filepath, algorithm)
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Checksum calculation failed: {e}")
            return result

        # Verify checksum match
        if result['actual_checksum'] != expected_checksum:
            result['valid'] = False
            result['errors'].append(
                f"Checksum mismatch: expected {expected_checksum}, "
                f"got {result['actual_checksum']}"
            )

        return result

    def detect_pdf_corruption(self, pdf_path: Path) -> Dict[str, any]:
        """
        Detect corruption in PDF files

        Args:
            pdf_path: Path to PDF file

        Returns:
            dict: Detection result with keys:
                - valid (bool): True if PDF is valid
                - errors (list): List of corruption issues
                - page_count (int): Number of pages (if valid)
        """
        result = {
            'valid': True,
            'errors': [],
            'page_count': 0
        }

        if not pdf_path.exists():
            result['valid'] = False
            result['errors'].append(f"File not found: {pdf_path}")
            return result

        # Check magic bytes (PDF header)
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    result['valid'] = False
                    result['errors'].append("Invalid PDF header (magic bytes missing)")
                    return result
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Could not read file header: {e}")
            return result

        # Deep PDF validation with PyPDF2
        if PDF_VALIDATION_AVAILABLE:
            try:
                reader = PdfReader(pdf_path)
                result['page_count'] = len(reader.pages)

                # Check if encrypted (could indicate corruption)
                if reader.is_encrypted:
                    logger.warning(f"PDF is encrypted: {pdf_path}")

                # Try to read first page (often fails on corrupted PDFs)
                if result['page_count'] > 0:
                    try:
                        _ = reader.pages[0].extract_text()
                    except Exception as e:
                        result['valid'] = False
                        result['errors'].append(f"Cannot read PDF content: {e}")

            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"PDF validation failed: {e}")
        else:
            logger.warning("PyPDF2 not available, skipping deep PDF validation")

        return result

    def detect_xml_corruption(self, xml_path: Path) -> Dict[str, any]:
        """
        Detect corruption in XML files

        Args:
            xml_path: Path to XML file

        Returns:
            dict: Detection result with keys:
                - valid (bool): True if XML is well-formed
                - errors (list): List of XML errors
                - root_tag (str): Root element tag name (if valid)
        """
        result = {
            'valid': True,
            'errors': [],
            'root_tag': None
        }

        if not xml_path.exists():
            result['valid'] = False
            result['errors'].append(f"File not found: {xml_path}")
            return result

        # XML validation with lxml
        if XML_VALIDATION_AVAILABLE:
            try:
                tree = etree.parse(str(xml_path))
                result['root_tag'] = tree.getroot().tag
            except etree.XMLSyntaxError as e:
                result['valid'] = False
                result['errors'].append(f"XML syntax error: {e}")
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"XML validation failed: {e}")
        else:
            # Basic well-formedness check without lxml
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(xml_path)
                result['root_tag'] = tree.getroot().tag
            except ET.ParseError as e:
                result['valid'] = False
                result['errors'].append(f"XML parsing error: {e}")
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"XML validation failed: {e}")

        return result

    def detect_json_corruption(self, json_path: Path) -> Dict[str, any]:
        """
        Detect corruption in JSON files

        Args:
            json_path: Path to JSON file

        Returns:
            dict: Detection result with keys:
                - valid (bool): True if JSON is valid
                - errors (list): List of JSON errors
        """
        result = {
            'valid': True,
            'errors': []
        }

        if not json_path.exists():
            result['valid'] = False
            result['errors'].append(f"File not found: {json_path}")
            return result

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['errors'].append(f"JSON decode error: {e}")
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"JSON validation failed: {e}")

        return result

    def quarantine_file(self,
                       filepath: Path,
                       reason: str,
                       metadata: Optional[Dict] = None):
        """
        Move corrupted or suspicious file to quarantine

        Args:
            filepath: Path to file to quarantine
            reason: Reason for quarantine
            metadata: Additional metadata (checksum, validation errors, etc.)
        """
        if not filepath.exists():
            logger.error(f"Cannot quarantine non-existent file: {filepath}")
            return

        # Generate quarantine filename
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        quarantine_path = self.quarantine_dir / f"{filepath.name}.{timestamp}.quarantine"

        # Move file to quarantine
        try:
            shutil.move(str(filepath), str(quarantine_path))
            logger.warning(f"File quarantined: {filepath} → {quarantine_path}")
        except Exception as e:
            logger.error(f"Failed to quarantine file: {e}")
            return

        # Write metadata file
        metadata_file = quarantine_path.with_suffix('.json')
        quarantine_metadata = {
            'original_path': str(filepath),
            'quarantine_path': str(quarantine_path),
            'quarantine_date': datetime.now(timezone.utc).isoformat(),
            'reason': reason,
            'metadata': metadata or {}
        }

        try:
            with open(metadata_file, 'w') as f:
                json.dump(quarantine_metadata, f, indent=2)
            logger.info(f"Quarantine metadata saved: {metadata_file}")
        except Exception as e:
            logger.error(f"Failed to write quarantine metadata: {e}")

    def create_bag(self,
                  resource_dir: Path,
                  resource_id: str,
                  metadata: Optional[Dict] = None) -> Optional[object]:
        """
        Create BagIt package for downloaded resource (RFC 8493)

        Args:
            resource_dir: Directory containing resource files
            resource_id: Resource identifier (e.g., 'RES-001')
            metadata: Additional bag metadata

        Returns:
            bagit.Bag object if successful, None otherwise
        """
        if not BAGIT_AVAILABLE:
            logger.error("BagIt library not available. Install with: pip install bagit")
            return None

        if not resource_dir.exists():
            logger.error(f"Resource directory not found: {resource_dir}")
            return None

        # Prepare bag info
        bag_info = {
            'Source-Organization': 'irStudy Medical Resources',
            'Contact-Name': 'Medical Resources Download System',
            'Resource-ID': resource_id,
            'Bagging-Date': datetime.now(timezone.utc).isoformat(),
        }

        # Add custom metadata
        if metadata:
            bag_info.update(metadata)

        try:
            # Create BagIt package
            bag = bagit.make_bag(
                str(resource_dir),
                checksums=['sha256', 'md5'],  # Both for compatibility
                bag_info=bag_info
            )

            logger.info(f"Created BagIt package for {resource_id} at {resource_dir}")
            return bag

        except Exception as e:
            logger.error(f"Failed to create BagIt package: {e}")
            return None

    def validate_bag(self, resource_dir: Path) -> Dict[str, any]:
        """
        Validate BagIt package integrity

        Args:
            resource_dir: Directory containing BagIt package

        Returns:
            dict: Validation result with keys:
                - valid (bool): True if all checksums match
                - errors (list): List of validation errors
        """
        result = {
            'valid': True,
            'errors': []
        }

        if not BAGIT_AVAILABLE:
            result['valid'] = False
            result['errors'].append("BagIt library not available")
            return result

        if not resource_dir.exists():
            result['valid'] = False
            result['errors'].append(f"Directory not found: {resource_dir}")
            return result

        try:
            bag = bagit.Bag(str(resource_dir))

            # Validate bag
            if bag.is_valid():
                logger.info(f"BagIt package valid: {resource_dir}")
            else:
                result['valid'] = False
                result['errors'].append("Bag validation failed (checksums don't match)")

        except bagit.BagError as e:
            result['valid'] = False
            result['errors'].append(f"BagIt validation error: {e}")
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Unexpected error: {e}")

        return result


def generate_manifest(resource_dir: Path,
                     resource_id: str,
                     algorithm: str = 'sha256') -> Dict:
    """
    Generate comprehensive file manifest for resource

    Args:
        resource_dir: Directory containing resource files
        resource_id: Resource identifier
        algorithm: Checksum algorithm

    Returns:
        dict: Manifest with file metadata
    """
    integrity_mgr = FileIntegrityManager()
    manifest = {
        'resource_id': resource_id,
        'manifest_version': '1.0',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'checksum_algorithm': algorithm,
        'files': []
    }

    if not resource_dir.exists():
        logger.error(f"Resource directory not found: {resource_dir}")
        return manifest

    # Scan all files
    for filepath in resource_dir.rglob('*'):
        if filepath.is_file() and not filepath.name.startswith('.'):
            # Calculate checksum
            try:
                checksum = integrity_mgr.calculate_checksum(filepath, algorithm)
                file_size = filepath.stat().st_size

                file_metadata = {
                    'file_id': filepath.name,
                    'file_path': str(filepath.relative_to(resource_dir)),
                    'file_size_bytes': file_size,
                    f'checksum_{algorithm}': checksum,
                    'downloaded_at': datetime.fromtimestamp(
                        filepath.stat().st_mtime, tz=timezone.utc
                    ).isoformat()
                }

                manifest['files'].append(file_metadata)

            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")

    # Calculate statistics
    manifest['statistics'] = {
        'total_files': len(manifest['files']),
        'total_size_bytes': sum(f['file_size_bytes'] for f in manifest['files']),
        'total_size_gb': sum(f['file_size_bytes'] for f in manifest['files']) / (1024**3)
    }

    return manifest


if __name__ == '__main__':
    # Example usage and testing
    import argparse

    parser = argparse.ArgumentParser(description='File integrity operations')
    parser.add_argument('command', choices=['checksum', 'validate', 'detect-corruption', 'create-bag', 'validate-bag', 'manifest'],
                       help='Command to execute')
    parser.add_argument('--file', type=Path, help='File path')
    parser.add_argument('--dir', type=Path, help='Directory path')
    parser.add_argument('--checksum', help='Expected checksum for validation')
    parser.add_argument('--algorithm', default='sha256', choices=['md5', 'sha256', 'sha512'],
                       help='Hash algorithm')
    parser.add_argument('--resource-id', help='Resource identifier')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    integrity_mgr = FileIntegrityManager()

    if args.command == 'checksum':
        if not args.file:
            print("Error: --file required")
            exit(1)
        checksum = integrity_mgr.calculate_checksum(args.file, args.algorithm)
        print(f"{args.algorithm}: {checksum}")

    elif args.command == 'validate':
        if not args.file or not args.checksum:
            print("Error: --file and --checksum required")
            exit(1)
        result = integrity_mgr.validate_file(args.file, args.checksum, args.algorithm)
        if result['valid']:
            print("✓ File is valid")
        else:
            print("✗ File is INVALID")
            for error in result['errors']:
                print(f"  - {error}")
            exit(1)

    elif args.command == 'detect-corruption':
        if not args.file:
            print("Error: --file required")
            exit(1)

        suffix = args.file.suffix.lower()
        if suffix == '.pdf':
            result = integrity_mgr.detect_pdf_corruption(args.file)
        elif suffix in ['.xml', '.html']:
            result = integrity_mgr.detect_xml_corruption(args.file)
        elif suffix == '.json':
            result = integrity_mgr.detect_json_corruption(args.file)
        else:
            print(f"Unsupported file type: {suffix}")
            exit(1)

        if result['valid']:
            print("✓ File is valid")
        else:
            print("✗ File is CORRUPTED")
            for error in result['errors']:
                print(f"  - {error}")
            exit(1)

    elif args.command == 'create-bag':
        if not args.dir or not args.resource_id:
            print("Error: --dir and --resource-id required")
            exit(1)
        bag = integrity_mgr.create_bag(args.dir, args.resource_id)
        if bag:
            print(f"✓ BagIt package created at {args.dir}")
        else:
            print("✗ Failed to create BagIt package")
            exit(1)

    elif args.command == 'validate-bag':
        if not args.dir:
            print("Error: --dir required")
            exit(1)
        result = integrity_mgr.validate_bag(args.dir)
        if result['valid']:
            print("✓ BagIt package is valid")
        else:
            print("✗ BagIt package is INVALID")
            for error in result['errors']:
                print(f"  - {error}")
            exit(1)

    elif args.command == 'manifest':
        if not args.dir or not args.resource_id:
            print("Error: --dir and --resource-id required")
            exit(1)
        manifest = generate_manifest(args.dir, args.resource_id, args.algorithm)
        manifest_file = args.dir / f"{args.resource_id}_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"✓ Manifest generated: {manifest_file}")
        print(f"  Files: {manifest['statistics']['total_files']}")
        print(f"  Total size: {manifest['statistics']['total_size_gb']:.2f} GB")
