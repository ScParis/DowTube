"""Rate limiter implementation using token bucket algorithm."""

import threading
import time
from typing import Optional
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter implementation.
    
    This class implements a thread-safe rate limiter using the token bucket algorithm.
    It helps prevent hitting API rate limits by controlling the rate of requests.
    
    Attributes:
        rate (int): Number of tokens to add per period
        period (int): Period in seconds
        burst (int): Maximum number of tokens that can be accumulated
        cooldown (int): Time to wait between retries when rate limited
    """
    
    def __init__(self, rate: int, period: int, burst: int, cooldown: int = 5):
        self.rate = float(rate)
        self.period = float(period)
        self.burst = float(burst)
        self.cooldown = cooldown
        self.tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()
        self._last_retry_time: Optional[datetime] = None
    
    def _add_tokens(self) -> None:
        """Add new tokens based on time passed."""
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * (self.rate / self.period)
        self.tokens = min(self.burst, self.tokens + new_tokens)
        self.last_update = now
    
    def _should_retry(self) -> bool:
        """Check if enough time has passed since last retry."""
        if self._last_retry_time is None:
            return True
        
        time_since_last = datetime.now() - self._last_retry_time
        return time_since_last.total_seconds() >= self.cooldown
    
    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire a token from the bucket.
        
        Args:
            block (bool): If True, block until a token is available
            timeout (float, optional): Maximum time to wait for a token
        
        Returns:
            bool: True if token was acquired, False otherwise
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                self._add_tokens()
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                
                if not block:
                    return False
                
                if not self._should_retry():
                    return False
                
                if timeout is not None:
                    if time.time() - start_time >= timeout:
                        return False
                
                self._last_retry_time = datetime.now()
            
            # Wait before next attempt
            time.sleep(self.cooldown)
    
    def try_acquire(self) -> bool:
        """Try to acquire a token without blocking.
        
        Returns:
            bool: True if token was acquired, False otherwise
        """
        return self.acquire(block=False)
