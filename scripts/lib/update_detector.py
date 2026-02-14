#!/usr/bin/env python3
"""
Resource Update Detector

Detects new and updated medical resources by querying APIs, scraping websites,
and checking HTTP headers.

Supports:
- StatPearls: NCBI E-utilities API for modification dates
- Cochrane: Website scraping or RSS feeds (if available)
- Guidelines: HTTP Last-Modified headers

Usage:
    from lib.update_detector import StatPearlsUpdateDetector

    detector = StatPearlsUpdateDetector(api_key='your_ncbi_key')
    updates = detector.get_updates_since(since_date='2026-01-10')
"""

import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Set
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class UpdateResult:
    """Result of update detection"""
    def __init__(self, resource_id: str, resource_name: str):
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.new_items: List[str] = []
        self.updated_items: List[str] = []
        self.total_items: int = 0
        self.error: Optional[str] = None

    def has_updates(self) -> bool:
        """Check if any updates were found"""
        return len(self.new_items) > 0 or len(self.updated_items) > 0

    def total_updates(self) -> int:
        """Total number of updates (new + updated)"""
        return len(self.new_items) + len(self.updated_items)


class ResourceUpdateDetector(ABC):
    """Base class for resource update detectors"""

    def __init__(self, resource_id: str, resource_name: str):
        self.resource_id = resource_id
        self.resource_name = resource_name

    @abstractmethod
    def detect_updates(self, since_date: Optional[datetime] = None, known_items: Optional[Set[str]] = None) -> UpdateResult:
        """
        Detect new and updated items.

        Args:
            since_date: Only check for items modified since this date
            known_items: Set of already-downloaded item IDs (to detect new ones)

        Returns:
            UpdateResult with new_items and updated_items lists
        """
        pass


class StatPearlsUpdateDetector(ResourceUpdateDetector):
    """
    Detect StatPearls updates via NCBI E-utilities API.

    The NCBI API provides:
    - esearch: Search for books with date filters
    - efetch: Get detailed metadata including modification dates
    - esummary: Get summary info (faster than efetch)

    Note: NCBI API rate limits:
    - Without key: 3 requests/second
    - With key: 10 requests/second
    """

    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("RES-001", "StatPearls Publishing Database")
        self.api_key = api_key
        self.rate_limit_delay = 0.1 if api_key else 0.34

    def _api_request(self, url: str, params: Dict) -> requests.Response:
        """Make rate-limited API request"""
        if self.api_key:
            params['api_key'] = self.api_key

        time.sleep(self.rate_limit_delay)
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response

    def get_all_statpearls_ids(self) -> List[str]:
        """Get all StatPearls book IDs"""
        params = {
            'db': 'books',
            'term': 'statpearls[book]',
            'retmax': 10000,
            'retmode': 'xml'
        }

        try:
            response = self._api_request(self.ESEARCH_URL, params)
            root = ET.fromstring(response.content)

            id_list = root.find('IdList')
            if id_list is None:
                return []

            book_ids = [id_elem.text for id_elem in id_list.findall('Id')]
            logger.info(f"Found {len(book_ids)} total StatPearls books")
            return book_ids

        except Exception as e:
            logger.error(f"Failed to get StatPearls IDs: {e}")
            return []

    def get_books_modified_since(self, since_date: datetime) -> List[str]:
        """
        Get StatPearls books modified since a specific date.

        Note: NCBI doesn't directly support "modified_since" in esearch,
        so we need to:
        1. Get all book IDs
        2. Query their modification dates via esummary
        3. Filter by date

        Alternative: Use reldate parameter for relative dates
        """
        # Convert date to NCBI reldate format (days ago)
        days_ago = (datetime.now(timezone.utc) - since_date).days

        if days_ago <= 0:
            logger.warning("Since date is in the future, checking last 7 days")
            days_ago = 7

        # Search with reldate (relative date)
        params = {
            'db': 'books',
            'term': 'statpearls[book]',
            'reldate': str(days_ago),
            'datetype': 'mdat',  # Modification date
            'retmax': 10000,
            'retmode': 'xml'
        }

        try:
            response = self._api_request(self.ESEARCH_URL, params)
            root = ET.fromstring(response.content)

            id_list = root.find('IdList')
            if id_list is None:
                logger.info("No books modified in the specified period")
                return []

            book_ids = [id_elem.text for id_elem in id_list.findall('Id')]
            logger.info(f"Found {len(book_ids)} books modified in last {days_ago} days")
            return book_ids

        except Exception as e:
            logger.error(f"Failed to get modified books: {e}")
            return []

    def detect_updates(self, since_date: Optional[datetime] = None, known_items: Optional[Set[str]] = None) -> UpdateResult:
        """
        Detect StatPearls updates.

        Args:
            since_date: Check for books modified since this date
            known_items: Set of already-downloaded book IDs

        Returns:
            UpdateResult with new and updated book IDs
        """
        result = UpdateResult(self.resource_id, self.resource_name)

        try:
            if since_date:
                # Get books modified since date
                modified_ids = set(self.get_books_modified_since(since_date))
                logger.info(f"Books modified since {since_date}: {len(modified_ids)}")

                if known_items:
                    # Separate new vs updated
                    result.new_items = list(modified_ids - known_items)
                    result.updated_items = list(modified_ids & known_items)
                else:
                    # If no known items, treat all as new
                    result.new_items = list(modified_ids)

            else:
                # Full scan: get all books
                all_ids = set(self.get_all_statpearls_ids())
                result.total_items = len(all_ids)

                if known_items:
                    result.new_items = list(all_ids - known_items)
                else:
                    result.new_items = list(all_ids)

            logger.info(f"StatPearls updates: {len(result.new_items)} new, {len(result.updated_items)} updated")

        except Exception as e:
            logger.error(f"Error detecting StatPearls updates: {e}")
            result.error = str(e)

        return result


class CochraneUpdateDetector(ResourceUpdateDetector):
    """
    Detect Cochrane review updates via website scraping or RSS.

    Options:
    1. RSS feed (if available): https://www.cochranelibrary.com/cdsr/rss
    2. Website search with date filter
    3. Manual export file (fallback)
    """

    RSS_URL = "https://www.cochranelibrary.com/cdsr/rss"
    SEARCH_URL = "https://www.cochranelibrary.com/cdsr/reviews"

    def __init__(self):
        super().__init__("RES-002", "Cochrane Systematic Reviews")

    def detect_updates(self, since_date: Optional[datetime] = None, known_items: Optional[Set[str]] = None) -> UpdateResult:
        """
        Detect Cochrane updates.

        Currently uses file-based approach (requires export file).
        Future enhancement: Implement RSS/scraping.
        """
        result = UpdateResult(self.resource_id, self.resource_name)

        # TODO: Implement RSS feed parsing or web scraping
        # For now, rely on manual export file
        logger.warning("Cochrane update detection not yet implemented")
        logger.info("Use download_cochrane_from_export.py with manual export file")

        result.error = "Automatic update detection not implemented - use export file"
        return result


class GuidelinesUpdateDetector(ResourceUpdateDetector):
    """
    Detect guidelines updates via HTTP Last-Modified headers.

    Checks:
    - RACGP Red Book
    - RANZCOG Guidelines
    - RANZCP Guidelines
    - Stroke Foundation
    - NSW Health
    - MeSH
    """

    def __init__(self, resource_id: str, resource_name: str, url: str):
        super().__init__(resource_id, resource_name)
        self.url = url

    def check_last_modified(self) -> Optional[datetime]:
        """Check Last-Modified header for resource"""
        try:
            response = requests.head(self.url, allow_redirects=True, timeout=10)
            response.raise_for_status()

            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                # Parse HTTP date format
                dt = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
                logger.info(f"{self.resource_name} last modified: {dt}")
                return dt
            else:
                logger.warning(f"No Last-Modified header for {self.resource_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to check {self.resource_name}: {e}")
            return None

    def detect_updates(self, since_date: Optional[datetime] = None, known_items: Optional[Set[str]] = None) -> UpdateResult:
        """
        Detect updates by comparing Last-Modified date.

        Returns:
            UpdateResult with updated_items containing [resource_id] if modified
        """
        result = UpdateResult(self.resource_id, self.resource_name)

        try:
            last_modified = self.check_last_modified()

            if last_modified and since_date:
                # Make since_date timezone-aware if needed
                if since_date.tzinfo is None:
                    since_date = since_date.replace(tzinfo=timezone.utc)
                if last_modified.tzinfo is None:
                    last_modified = last_modified.replace(tzinfo=timezone.utc)

                if last_modified > since_date:
                    result.updated_items = [self.resource_id]
                    logger.info(f"✨ {self.resource_name} has been updated!")
                else:
                    logger.info(f"✓ {self.resource_name} is up-to-date")
            elif last_modified:
                # No since_date provided, assume needs download
                result.new_items = [self.resource_id]

        except Exception as e:
            logger.error(f"Error detecting updates for {self.resource_name}: {e}")
            result.error = str(e)

        return result


def create_detector(resource_id: str, resource_info: Dict, api_key: Optional[str] = None) -> Optional[ResourceUpdateDetector]:
    """
    Factory function to create appropriate detector for a resource.

    Args:
        resource_id: Resource identifier (e.g., "RES-001")
        resource_info: Resource information from resource_database.json
        api_key: NCBI API key (for StatPearls)

    Returns:
        Appropriate ResourceUpdateDetector subclass or None
    """
    resource_name = resource_info.get('name', '')

    if resource_id == "RES-001":  # StatPearls
        return StatPearlsUpdateDetector(api_key=api_key)

    elif resource_id == "RES-002":  # Cochrane
        return CochraneUpdateDetector()

    elif resource_id in ["RES-003", "RES-004", "RES-005", "RES-006", "RES-008", "RES-009"]:
        # Guidelines with direct URLs
        url = resource_info.get('url')
        if url:
            return GuidelinesUpdateDetector(resource_id, resource_name, url)

    logger.warning(f"No detector available for {resource_id} ({resource_name})")
    return None
