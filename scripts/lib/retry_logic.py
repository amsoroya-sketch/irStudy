#!/usr/bin/env python3
"""
Retry Logic and Circuit Breakers for Medical Resources Download System

Implements resilient download strategies with:
- Exponential backoff (2^n retry delay)
- Circuit breakers (fail-fast when service is down)
- Adaptive rate limiting (handle 429 responses)
- Jitter (randomization to prevent thundering herd)

Industry Standards:
- AWS Retry Strategy: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- Google Cloud Retry: https://cloud.google.com/storage/docs/retry-strategy
- Tenacity library: https://tenacity.readthedocs.io/

Usage:
    from scripts.lib.retry_logic import (
        retry_with_backoff,
        resilient_session,
        CircuitBreaker
    )

    # Method 1: Decorator
    @retry_with_backoff(max_attempts=3)
    def download_file(url):
        return requests.get(url)

    # Method 2: Resilient session
    session = resilient_session(max_retries=5)
    response = session.get(url)

    # Method 3: Circuit breaker
    breaker = CircuitBreaker(fail_threshold=5, timeout=60)
    with breaker:
        response = requests.get(url)
"""

import time
import random
import logging
from typing import Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

logger = logging.getLogger(__name__)


# ==================== Exponential Backoff Decorator ====================

def retry_with_backoff(max_attempts: int = 3,
                      initial_delay: float = 1.0,
                      max_delay: float = 60.0,
                      exponential_base: float = 2.0,
                      jitter: bool = True):
    """
    Decorator for exponential backoff retry logic

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (default 1.0)
        max_delay: Maximum delay in seconds (default 60.0)
        exponential_base: Base for exponential calculation (default 2.0)
        jitter: Add randomization to prevent thundering herd (default True)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_attempts=5)
        def download_file(url):
            return requests.get(url)
    """
    if jitter:
        # Use random exponential with jitter (AWS recommendation)
        wait_strategy = wait_random_exponential(
            multiplier=initial_delay,
            max=max_delay
        )
    else:
        # Use fixed exponential without jitter
        wait_strategy = wait_exponential(
            multiplier=initial_delay,
            min=initial_delay,
            max=max_delay,
            exp_base=exponential_base
        )

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_strategy,
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )


# ==================== Resilient HTTP Session ====================

def resilient_session(max_retries: int = 5,
                     backoff_factor: float = 1.0,
                     status_forcelist: Optional[list] = None) -> requests.Session:
    """
    Create HTTP session with automatic retry logic

    Args:
        max_retries: Maximum number of retries (default 5)
        backoff_factor: Backoff multiplier (default 1.0)
                       Delays: 1s, 2s, 4s, 8s, 16s
        status_forcelist: HTTP status codes to retry (default [429, 500, 502, 503, 504])

    Returns:
        requests.Session with retry configuration

    Example:
        session = resilient_session(max_retries=3)
        response = session.get('https://api.example.com/data')
    """
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]

    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD"],  # Retry safe methods
        raise_on_status=False  # Don't raise exception, let caller handle
    )

    # Create HTTP adapter with retry
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Create session
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set reasonable timeout (connection, read)
    session.request = _add_timeout_to_request(session.request)

    return session


def _add_timeout_to_request(original_request: Callable) -> Callable:
    """Add default timeout to requests.Session.request method"""
    @wraps(original_request)
    def request_with_timeout(*args, **kwargs):
        # Set default timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (10, 30)  # (connect timeout, read timeout)
        return original_request(*args, **kwargs)
    return request_with_timeout


# ==================== Circuit Breaker ====================

class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern for failing fast when service is down

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is down, fail immediately
    - HALF_OPEN: Testing if service recovered

    Args:
        fail_threshold: Number of failures before opening circuit (default 5)
        timeout: Time in seconds to wait before testing recovery (default 60)
        success_threshold: Successes needed in HALF_OPEN to close circuit (default 2)

    Example:
        breaker = CircuitBreaker(fail_threshold=3, timeout=30)

        try:
            with breaker:
                response = requests.get(url)
        except CircuitBreakerError:
            logger.error("Service is down, skipping request")
    """

    STATE_CLOSED = 'CLOSED'
    STATE_OPEN = 'OPEN'
    STATE_HALF_OPEN = 'HALF_OPEN'

    def __init__(self,
                 fail_threshold: int = 5,
                 timeout: int = 60,
                 success_threshold: int = 2):
        self.fail_threshold = fail_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.state = self.STATE_CLOSED
        self.fail_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def __enter__(self):
        """Context manager entry"""
        # Check if we should transition from OPEN to HALF_OPEN
        if self.state == self.STATE_OPEN:
            if self._should_attempt_reset():
                logger.info("Circuit breaker: Transitioning to HALF_OPEN (testing recovery)")
                self.state = self.STATE_HALF_OPEN
                self.success_count = 0
            else:
                # Still in cooldown period
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN (service down). "
                    f"Will retry after {self._time_until_retry():.0f}s"
                )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record success or failure"""
        if exc_type is None:
            # Success
            self._record_success()
            return False  # Don't suppress exceptions
        else:
            # Failure
            self._record_failure()
            return False  # Don't suppress exceptions

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try resetting circuit"""
        if self.last_failure_time is None:
            return True

        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.timeout

    def _time_until_retry(self) -> float:
        """Calculate seconds until next retry attempt"""
        if self.last_failure_time is None:
            return 0.0

        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0.0, self.timeout - time_since_failure)

    def _record_success(self):
        """Record successful request"""
        if self.state == self.STATE_HALF_OPEN:
            self.success_count += 1
            logger.info(f"Circuit breaker: Success {self.success_count}/{self.success_threshold}")

            # Close circuit if enough successes
            if self.success_count >= self.success_threshold:
                logger.info("Circuit breaker: CLOSED (service recovered)")
                self.state = self.STATE_CLOSED
                self.fail_count = 0
                self.success_count = 0

        elif self.state == self.STATE_CLOSED:
            # Reset failure count on success
            self.fail_count = 0

    def _record_failure(self):
        """Record failed request"""
        self.fail_count += 1
        self.last_failure_time = datetime.now()

        if self.state == self.STATE_HALF_OPEN:
            # Failure in HALF_OPEN state - reopen circuit
            logger.warning("Circuit breaker: OPEN (service still down)")
            self.state = self.STATE_OPEN
            self.success_count = 0

        elif self.state == self.STATE_CLOSED:
            # Check if we should open circuit
            if self.fail_count >= self.fail_threshold:
                logger.error(
                    f"Circuit breaker: OPEN (threshold reached: {self.fail_count} failures). "
                    f"Will retry in {self.timeout}s"
                )
                self.state = self.STATE_OPEN

    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state

    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        logger.info("Circuit breaker: Manually reset to CLOSED")
        self.state = self.STATE_CLOSED
        self.fail_count = 0
        self.success_count = 0
        self.last_failure_time = None


# ==================== Adaptive Rate Limiter ====================

class AdaptiveRateLimiter:
    """
    Rate limiter with automatic adjustment based on 429 responses

    Features:
    - Respects server rate limits (429 responses)
    - Exponential backoff when rate limited
    - Automatic recovery when limits clear

    Args:
        requests_per_second: Initial rate limit (default 10.0)
        max_backoff: Maximum backoff time in seconds (default 300.0 = 5 minutes)

    Example:
        limiter = AdaptiveRateLimiter(requests_per_second=10.0)

        for url in urls:
            limiter.wait()  # Enforces rate limit
            response = requests.get(url)

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                limiter.handle_rate_limit(retry_after)
    """

    def __init__(self,
                 requests_per_second: float = 10.0,
                 max_backoff: float = 300.0):
        self.requests_per_second = requests_per_second
        self.min_delay = 1.0 / requests_per_second
        self.max_backoff = max_backoff
        self.current_backoff = 0.0
        self.last_request_time = 0.0

    def wait(self):
        """Wait appropriate time before next request"""
        now = time.time()

        # Enforce minimum delay between requests
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)

        # Add backoff if we've been rate limited
        if self.current_backoff > 0:
            logger.warning(f"Rate limited - backing off for {self.current_backoff:.1f}s")
            time.sleep(self.current_backoff)

        self.last_request_time = time.time()

    def handle_rate_limit(self, retry_after: Optional[int] = None):
        """
        Handle 429 rate limit response

        Args:
            retry_after: Seconds to wait (from Retry-After header)
        """
        if retry_after:
            # Server told us how long to wait
            self.current_backoff = min(retry_after, self.max_backoff)
        else:
            # Exponential backoff: 60s, 120s, 240s, ...
            if self.current_backoff == 0:
                self.current_backoff = 60.0
            else:
                self.current_backoff = min(self.current_backoff * 2, self.max_backoff)

        logger.error(
            f"Rate limit hit! Backing off for {self.current_backoff:.1f}s "
            f"(retry_after={retry_after})"
        )

    def reset(self):
        """Reset backoff after successful request"""
        if self.current_backoff > 0:
            logger.info("Rate limit cleared, resetting backoff")
            self.current_backoff = 0.0


# ==================== Smart Retry with Context ====================

class SmartRetrySession(requests.Session):
    """
    Enhanced session with retry logic, circuit breaker, and rate limiting

    Combines all resilience patterns:
    - Automatic retries with exponential backoff
    - Circuit breaker for failing services
    - Adaptive rate limiting
    - Audit logging integration

    Example:
        session = SmartRetrySession(
            resource_id='RES-001',
            max_retries=5,
            rate_limit=10.0
        )

        response = session.get('https://api.example.com/data')
    """

    def __init__(self,
                 resource_id: str,
                 max_retries: int = 5,
                 rate_limit: float = 10.0,
                 circuit_breaker: Optional[CircuitBreaker] = None,
                 audit_logger: Optional[object] = None):
        super().__init__()

        self.resource_id = resource_id
        self.audit_logger = audit_logger

        # Set up retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

        # Initialize rate limiter
        self.rate_limiter = AdaptiveRateLimiter(requests_per_second=rate_limit)

        # Initialize circuit breaker
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            fail_threshold=5,
            timeout=60
        )

    def request(self, method, url, **kwargs):
        """Override request method to add resilience features"""
        # Enforce rate limiting
        self.rate_limiter.wait()

        # Check circuit breaker
        try:
            with self.circuit_breaker:
                # Make request
                response = super().request(method, url, **kwargs)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.rate_limiter.handle_rate_limit(retry_after)

                    # Log rate limit
                    if self.audit_logger:
                        self.audit_logger.log_rate_limit_hit(self.resource_id, retry_after)

                # Success - reset rate limiter
                elif response.ok:
                    self.rate_limiter.reset()

                return response

        except CircuitBreakerError as e:
            # Log circuit breaker open
            if self.audit_logger:
                self.audit_logger.log_security_event(
                    'CIRCUIT_BREAKER_OPEN',
                    self.resource_id,
                    {'url': url, 'error': str(e)}
                )
            raise


if __name__ == '__main__':
    # Example usage and testing
    import argparse

    parser = argparse.ArgumentParser(description='Test retry logic and circuit breakers')
    parser.add_argument('command', choices=['test-retry', 'test-circuit-breaker', 'test-rate-limiter'],
                       help='Test to run')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if args.command == 'test-retry':
        print("Testing retry with exponential backoff...")

        @retry_with_backoff(max_attempts=3)
        def flaky_function():
            """Simulate flaky API that fails randomly"""
            if random.random() < 0.7:  # 70% failure rate
                raise requests.exceptions.ConnectionError("Simulated network error")
            return "Success!"

        try:
            result = flaky_function()
            print(f"✓ Success: {result}")
        except Exception as e:
            print(f"✗ Failed after retries: {e}")

    elif args.command == 'test-circuit-breaker':
        print("Testing circuit breaker...")

        breaker = CircuitBreaker(fail_threshold=3, timeout=10)

        for i in range(10):
            try:
                with breaker:
                    # Simulate failing service
                    if i < 5:  # Fail first 5 attempts
                        raise Exception("Service down")
                    print(f"Request {i}: Success")
                    time.sleep(1)
            except (CircuitBreakerError, Exception) as e:
                print(f"Request {i}: {type(e).__name__} - {e}")
                time.sleep(1)

    elif args.command == 'test-rate-limiter':
        print("Testing adaptive rate limiter...")

        limiter = AdaptiveRateLimiter(requests_per_second=5.0)

        # Simulate API calls
        for i in range(10):
            limiter.wait()
            print(f"Request {i} at {time.time():.2f}")

            # Simulate rate limit on 5th request
            if i == 5:
                print("  → Simulating 429 response")
                limiter.handle_rate_limit(retry_after=3)
