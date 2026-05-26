# utils.py — Retry decorator, Circuit breaker, helpers

import time
import hashlib
from datetime import datetime, timezone, timedelta
from functools import wraps
from config import Config
from exceptions import RetryExhaustedError, CircuitBreakerOpenError
from logger import log


def retry(max_retries=None, delay=None, backoff=None, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    max_retries = max_retries or Config.MAX_RETRIES
    delay = delay or Config.RETRY_DELAY
    backoff = backoff or Config.RETRY_BACKOFF

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        log.error(f"❌ {func.__name__} failed after {max_retries} retries: {e}")
                        raise RetryExhaustedError(func.__name__, max_retries)
                    log.warning(f"⚠️ {func.__name__} attempt {attempt}/{max_retries} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern — stop calling a failing service."""

    def __init__(self, name, threshold=None, timeout=None):
        self.name = name
        self.threshold = threshold or Config.CB_THRESHOLD
        self.timeout = timeout or Config.CB_TIMEOUT
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED = normal, OPEN = blocked, HALF_OPEN = testing

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                log.info(f"🔄 Circuit breaker {self.name}: HALF_OPEN (testing)")
            else:
                raise CircuitBreakerOpenError(self.name)

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                log.info(f"✅ Circuit breaker {self.name}: CLOSED (recovered)")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.threshold:
                self.state = "OPEN"
                log.error(f"🔴 Circuit breaker {self.name}: OPEN after {self.failure_count} failures")
            raise


def generate_sms_hash(sms_body):
    """Generate MD5 hash for duplicate SMS detection."""
    cleaned = sms_body.strip().lower()
    return hashlib.md5(cleaned.encode()).hexdigest()


def to_ist(utc_time):
    """Convert UTC datetime to IST."""
    ist = timezone(timedelta(hours=5, minutes=30))
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(ist)


def to_utc(ist_time):
    """Convert IST datetime to UTC."""
    return ist_time.astimezone(timezone.utc)