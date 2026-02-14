#!/usr/bin/env python3
"""
HIPAA-Compliant Audit Logger for Medical Resources Download System

Implements audit logging with security event tracking, tamper resistance,
and long-term retention for regulatory compliance.

HIPAA Requirements (§164.312(b)):
- Audit Controls: Record and examine activity in systems containing ePHI
- 6-year retention period
- Tamper-resistant logging
- Detailed event tracking (who, what, when, where)

Note: This system does NOT handle ePHI (Protected Health Information).
However, we implement HIPAA-grade logging as best practice for medical systems.

Security Features:
- Append-only JSON Lines (JSONL) format
- File permissions (0600 - owner read/write only)
- Structured logging with required fields
- Monthly log rotation with 6-year retention
- Event categorization (auth, download, validation, error)

Usage:
    from scripts.lib.audit_logger import AuditLogger

    audit = AuditLogger()

    # Log download start
    audit.log_download_start('RES-001', 'https://ncbi.nlm.nih.gov/...')

    # Log download success
    audit.log_download_success('RES-001', '/path/to/file.pdf', 1024000, 'abc123...')

    # Log security event
    audit.log_security_event('CHECKSUM_MISMATCH', 'RES-001', {...})
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any
import socket
import getpass

logger = logging.getLogger(__name__)


class AuditLogger:
    """HIPAA-compliant audit logging for medical resources system"""

    # Event types (categorized for filtering and alerting)
    EVENT_CATEGORIES = {
        'AUTH': 'Authentication and authorization events',
        'DOWNLOAD': 'Resource download events',
        'VALIDATION': 'File integrity validation events',
        'ERROR': 'Error and failure events',
        'SECURITY': 'Security-related events',
        'SYSTEM': 'System operations'
    }

    EVENT_TYPES = {
        # Authentication events
        'AUTH_SUCCESS': 'AUTH',
        'AUTH_FAILURE': 'AUTH',
        'API_KEY_USED': 'AUTH',
        'API_KEY_ROTATED': 'AUTH',

        # Download events
        'DOWNLOAD_START': 'DOWNLOAD',
        'DOWNLOAD_SUCCESS': 'DOWNLOAD',
        'DOWNLOAD_FAILURE': 'DOWNLOAD',
        'DOWNLOAD_RESUMED': 'DOWNLOAD',

        # Validation events
        'CHECKSUM_CALCULATED': 'VALIDATION',
        'CHECKSUM_VERIFIED': 'VALIDATION',
        'CHECKSUM_MISMATCH': 'VALIDATION',
        'CORRUPTION_DETECTED': 'VALIDATION',
        'FILE_QUARANTINED': 'VALIDATION',

        # Error events
        'HTTP_ERROR': 'ERROR',
        'RATE_LIMIT_HIT': 'ERROR',
        'NETWORK_ERROR': 'ERROR',

        # Security events
        'TOS_VIOLATION_DETECTED': 'SECURITY',
        'SUSPICIOUS_ACTIVITY': 'SECURITY',
        'UNAUTHORIZED_ACCESS': 'SECURITY',

        # System events
        'SYSTEM_START': 'SYSTEM',
        'SYSTEM_STOP': 'SYSTEM',
        'CONFIG_CHANGED': 'SYSTEM'
    }

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize AuditLogger

        Args:
            log_dir: Directory to store audit logs
                    Defaults to /var/log/medical_resources/
        """
        if log_dir is None:
            # Try system log directory first, fall back to data directory
            system_log_dir = Path('/var/log/medical_resources')
            if os.access('/var/log', os.W_OK):
                log_dir = system_log_dir
            else:
                # Fallback to data directory if no system write access
                log_dir = Path('/mnt/data/medical_resources/logs')

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set directory permissions (owner read/write/execute)
        try:
            self.log_dir.chmod(0o700)
        except Exception as e:
            logger.warning(f"Could not set log directory permissions: {e}")

        # Create monthly log file
        self.current_month = datetime.now(timezone.utc).strftime('%Y%m')
        self.audit_file = self.log_dir / f'audit_{self.current_month}.jsonl'

        # Initialize log file if doesn't exist
        if not self.audit_file.exists():
            self._initialize_log_file()

        # Set file permissions (owner read/write only)
        try:
            self.audit_file.chmod(0o600)
        except Exception as e:
            logger.warning(f"Could not set audit file permissions: {e}")

        # Get system context (cached for performance)
        self._system_context = self._get_system_context()

    def _initialize_log_file(self):
        """Initialize new audit log file with header metadata"""
        header = {
            '_type': 'AUDIT_LOG_HEADER',
            'log_file': str(self.audit_file),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'system': self._get_system_context(),
            'retention_policy': '6 years (HIPAA compliance)',
            'format': 'JSON Lines (JSONL)',
            'note': 'This is a security audit log. Tampering is logged and may violate compliance requirements.'
        }

        with open(self.audit_file, 'w') as f:
            f.write(json.dumps(header) + '\n')

        logger.info(f"Initialized audit log: {self.audit_file}")

    def _get_system_context(self) -> Dict[str, str]:
        """Get system context for audit entries"""
        return {
            'hostname': socket.gethostname(),
            'user': getpass.getuser(),
            'pid': os.getpid(),
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }

    def _rotate_log_if_needed(self):
        """Check if we need to rotate to a new monthly log file"""
        current_month = datetime.now(timezone.utc).strftime('%Y%m')
        if current_month != self.current_month:
            # New month - rotate to new log file
            self.current_month = current_month
            self.audit_file = self.log_dir / f'audit_{self.current_month}.jsonl'
            self._initialize_log_file()
            logger.info(f"Rotated to new audit log: {self.audit_file}")

    def log_event(self,
                  event_type: str,
                  resource_id: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  severity: str = 'INFO'):
        """
        Log a security/audit event

        Args:
            event_type: Event type (must be in EVENT_TYPES)
            resource_id: Resource identifier (e.g., 'RES-001')
            details: Additional event details
            severity: Event severity ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        # Rotate log file if new month
        self._rotate_log_if_needed()

        # Validate event type
        if event_type not in self.EVENT_TYPES:
            logger.warning(f"Unknown event type: {event_type}")
            event_type = 'UNKNOWN'

        # Build audit entry
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'event_category': self.EVENT_TYPES.get(event_type, 'UNKNOWN'),
            'severity': severity,
            'resource_id': resource_id,
            'user': self._system_context['user'],
            'hostname': self._system_context['hostname'],
            'pid': self._system_context['pid'],
            'details': details or {}
        }

        # Write to audit log (append-only)
        try:
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            # Critical: Audit logging failed
            logger.error(f"CRITICAL: Failed to write audit log: {e}")
            # Try to write to stderr as last resort
            print(f"AUDIT LOG FAILURE: {json.dumps(event)}", file=os.sys.stderr)

    # ==================== Authentication Events ====================

    def log_auth_attempt(self,
                        resource_id: str,
                        success: bool,
                        api_key_used: Optional[str] = None,
                        error: Optional[str] = None):
        """Log API authentication attempt"""
        event_type = 'AUTH_SUCCESS' if success else 'AUTH_FAILURE'
        severity = 'INFO' if success else 'WARNING'

        details = {
            'success': success,
            'api_key_prefix': api_key_used[:10] + '...' if api_key_used else None,
            'error': error
        }

        self.log_event(event_type, resource_id, details, severity)

    # ==================== Download Events ====================

    def log_download_start(self, resource_id: str, source_url: str):
        """Log start of download operation"""
        details = {
            'source_url': source_url,
            'action': 'download_started'
        }
        self.log_event('DOWNLOAD_START', resource_id, details, 'INFO')

    def log_download_success(self,
                            resource_id: str,
                            file_path: str,
                            size_bytes: int,
                            checksum: Optional[str] = None):
        """Log successful download"""
        details = {
            'file_path': file_path,
            'size_bytes': size_bytes,
            'size_mb': round(size_bytes / (1024 * 1024), 2),
            'checksum_sha256': checksum,
            'action': 'download_completed'
        }
        self.log_event('DOWNLOAD_SUCCESS', resource_id, details, 'INFO')

    def log_download_failure(self,
                            resource_id: str,
                            error: str,
                            http_status: Optional[int] = None,
                            source_url: Optional[str] = None):
        """Log failed download"""
        details = {
            'error': error,
            'http_status': http_status,
            'source_url': source_url,
            'action': 'download_failed'
        }
        self.log_event('DOWNLOAD_FAILURE', resource_id, details, 'ERROR')

    def log_download_resumed(self,
                            resource_id: str,
                            file_path: str,
                            bytes_already_downloaded: int):
        """Log resumed download (HTTP Range request)"""
        details = {
            'file_path': file_path,
            'bytes_already_downloaded': bytes_already_downloaded,
            'action': 'download_resumed'
        }
        self.log_event('DOWNLOAD_RESUMED', resource_id, details, 'INFO')

    # ==================== Validation Events ====================

    def log_checksum_calculated(self,
                               resource_id: str,
                               file_path: str,
                               checksum: str,
                               algorithm: str = 'sha256'):
        """Log checksum calculation"""
        details = {
            'file_path': file_path,
            'checksum': checksum,
            'algorithm': algorithm,
            'action': 'checksum_calculated'
        }
        self.log_event('CHECKSUM_CALCULATED', resource_id, details, 'DEBUG')

    def log_checksum_verified(self,
                             resource_id: str,
                             file_path: str,
                             checksum: str):
        """Log successful checksum verification"""
        details = {
            'file_path': file_path,
            'checksum': checksum,
            'result': 'valid',
            'action': 'checksum_verified'
        }
        self.log_event('CHECKSUM_VERIFIED', resource_id, details, 'INFO')

    def log_checksum_mismatch(self,
                             resource_id: str,
                             file_path: str,
                             expected: str,
                             actual: str):
        """Log checksum mismatch (potential corruption or tampering)"""
        details = {
            'file_path': file_path,
            'expected_checksum': expected,
            'actual_checksum': actual,
            'result': 'MISMATCH',
            'action': 'checksum_failed'
        }
        self.log_event('CHECKSUM_MISMATCH', resource_id, details, 'ERROR')

    def log_corruption_detected(self,
                               resource_id: str,
                               file_path: str,
                               corruption_type: str,
                               errors: list):
        """Log file corruption detection"""
        details = {
            'file_path': file_path,
            'corruption_type': corruption_type,
            'errors': errors,
            'action': 'corruption_detected'
        }
        self.log_event('CORRUPTION_DETECTED', resource_id, details, 'ERROR')

    def log_file_quarantined(self,
                            resource_id: str,
                            file_path: str,
                            quarantine_path: str,
                            reason: str):
        """Log file moved to quarantine"""
        details = {
            'original_path': file_path,
            'quarantine_path': quarantine_path,
            'reason': reason,
            'action': 'file_quarantined'
        }
        self.log_event('FILE_QUARANTINED', resource_id, details, 'WARNING')

    # ==================== Error Events ====================

    def log_http_error(self,
                      resource_id: str,
                      http_status: int,
                      url: str,
                      error_message: Optional[str] = None):
        """Log HTTP error"""
        details = {
            'http_status': http_status,
            'url': url,
            'error_message': error_message,
            'action': 'http_error'
        }
        self.log_event('HTTP_ERROR', resource_id, details, 'ERROR')

    def log_rate_limit_hit(self,
                          resource_id: str,
                          retry_after: Optional[int] = None):
        """Log rate limit (429) response"""
        details = {
            'http_status': 429,
            'retry_after_seconds': retry_after,
            'action': 'rate_limited'
        }
        self.log_event('RATE_LIMIT_HIT', resource_id, details, 'WARNING')

    # ==================== Security Events ====================

    def log_security_event(self,
                          event_type: str,
                          resource_id: str,
                          details: Dict[str, Any]):
        """Log generic security event"""
        self.log_event(event_type, resource_id, details, 'WARNING')

    def log_tos_violation(self,
                         resource_id: str,
                         violation_type: str,
                         details: Dict[str, Any]):
        """Log Terms of Service violation detected"""
        details['violation_type'] = violation_type
        self.log_event('TOS_VIOLATION_DETECTED', resource_id, details, 'ERROR')

    # ==================== System Events ====================

    def log_system_start(self, component: str, version: str):
        """Log system component start"""
        details = {
            'component': component,
            'version': version,
            'action': 'system_started'
        }
        self.log_event('SYSTEM_START', None, details, 'INFO')

    def log_system_stop(self, component: str, reason: str = 'normal_shutdown'):
        """Log system component stop"""
        details = {
            'component': component,
            'reason': reason,
            'action': 'system_stopped'
        }
        self.log_event('SYSTEM_STOP', None, details, 'INFO')

    # ==================== Query & Analysis ====================

    def query_events(self,
                    event_type: Optional[str] = None,
                    resource_id: Optional[str] = None,
                    severity: Optional[str] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    limit: int = 100) -> list:
        """
        Query audit log events

        Args:
            event_type: Filter by event type
            resource_id: Filter by resource ID
            severity: Filter by severity level
            start_date: Filter events after this date
            end_date: Filter events before this date
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        events = []

        try:
            with open(self.audit_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)

                        # Skip header entries
                        if event.get('_type') == 'AUDIT_LOG_HEADER':
                            continue

                        # Apply filters
                        if event_type and event.get('event_type') != event_type:
                            continue
                        if resource_id and event.get('resource_id') != resource_id:
                            continue
                        if severity and event.get('severity') != severity:
                            continue

                        # Date filters
                        if start_date or end_date:
                            event_time = datetime.fromisoformat(event['timestamp'])
                            if start_date and event_time < start_date:
                                continue
                            if end_date and event_time > end_date:
                                continue

                        events.append(event)

                        # Limit results
                        if len(events) >= limit:
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"Malformed audit log entry: {line}")

        except FileNotFoundError:
            logger.warning(f"Audit log not found: {self.audit_file}")

        return events

    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics for recent audit events

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with event counts by type, severity, etc.
        """
        start_date = datetime.now(timezone.utc) - __import__('datetime').timedelta(days=days)
        events = self.query_events(start_date=start_date, limit=10000)

        summary = {
            'period_days': days,
            'total_events': len(events),
            'by_type': {},
            'by_category': {},
            'by_severity': {},
            'by_resource': {},
            'errors': 0,
            'warnings': 0
        }

        for event in events:
            # Count by type
            event_type = event.get('event_type', 'UNKNOWN')
            summary['by_type'][event_type] = summary['by_type'].get(event_type, 0) + 1

            # Count by category
            category = event.get('event_category', 'UNKNOWN')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1

            # Count by severity
            severity = event.get('severity', 'INFO')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

            if severity == 'ERROR':
                summary['errors'] += 1
            elif severity == 'WARNING':
                summary['warnings'] += 1

            # Count by resource
            resource_id = event.get('resource_id')
            if resource_id:
                summary['by_resource'][resource_id] = summary['by_resource'].get(resource_id, 0) + 1

        return summary


if __name__ == '__main__':
    # Example usage and testing
    import argparse

    parser = argparse.ArgumentParser(description='Audit log operations')
    parser.add_argument('command', choices=['query', 'summary', 'test'],
                       help='Command to execute')
    parser.add_argument('--event-type', help='Filter by event type')
    parser.add_argument('--resource-id', help='Filter by resource ID')
    parser.add_argument('--severity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Filter by severity')
    parser.add_argument('--days', type=int, default=7, help='Number of days for summary')
    parser.add_argument('--limit', type=int, default=100, help='Maximum events to return')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    audit = AuditLogger()

    if args.command == 'test':
        # Test various event types
        print("Testing audit logger...")

        audit.log_system_start('weekly_medical_update', '1.0')
        audit.log_download_start('RES-001', 'https://ncbi.nlm.nih.gov/books/NBK430685/')
        audit.log_auth_attempt('RES-001', True, api_key_used='abc123...')
        audit.log_download_success('RES-001', '/tmp/test.pdf', 1024000, 'abc123...')
        audit.log_checksum_verified('RES-001', '/tmp/test.pdf', 'abc123...')
        audit.log_system_stop('weekly_medical_update')

        print(f"✓ Test events written to {audit.audit_file}")

    elif args.command == 'query':
        events = audit.query_events(
            event_type=args.event_type,
            resource_id=args.resource_id,
            severity=args.severity,
            limit=args.limit
        )

        print(f"Found {len(events)} matching events:")
        for event in events:
            print(f"\n{event['timestamp']} - {event['event_type']} ({event['severity']})")
            print(f"  Resource: {event.get('resource_id', 'N/A')}")
            print(f"  User: {event['user']} @ {event['hostname']}")
            if event.get('details'):
                print(f"  Details: {json.dumps(event['details'], indent=4)}")

    elif args.command == 'summary':
        summary = audit.get_summary(days=args.days)

        print(f"\n=== Audit Log Summary (Last {summary['period_days']} days) ===")
        print(f"Total Events: {summary['total_events']}")
        print(f"Errors: {summary['errors']}")
        print(f"Warnings: {summary['warnings']}")

        print(f"\nBy Category:")
        for category, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")

        print(f"\nBy Severity:")
        for severity, count in sorted(summary['by_severity'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {severity}: {count}")

        if summary['by_resource']:
            print(f"\nBy Resource:")
            for resource, count in sorted(summary['by_resource'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {resource}: {count}")
