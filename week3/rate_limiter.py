"""
Rate limiting utilities for API calls with exponential backoff.
"""

import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class RateLimitStatus(Enum):
    """Rate limit status"""
    OK = "ok"
    WARNING = "warning"
    EXCEEDED = "exceeded"


@dataclass
class RateLimitInfo:
    """Rate limit information"""
    status: RateLimitStatus
    remaining: int
    reset_time: float
    retry_after: Optional[float] = None


class RateLimiter:
    """Rate limiter with exponential backoff"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[float] = []
        self.backoff_multiplier = 1.5
        self.max_backoff = 60  # Maximum 60 seconds backoff
    
    def _clean_old_requests(self, current_time: float) -> None:
        """Remove requests older than the time window"""
        cutoff = current_time - self.time_window
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
    
    def check_rate_limit(self) -> RateLimitInfo:
        """Check current rate limit status"""
        current_time = time.time()
        self._clean_old_requests(current_time)
        
        remaining = self.max_requests - len(self.requests)
        
        if len(self.requests) >= self.max_requests:
            # Rate limit exceeded
            oldest_request = min(self.requests)
            reset_time = oldest_request + self.time_window
            retry_after = reset_time - current_time
            
            return RateLimitInfo(
                status=RateLimitStatus.EXCEEDED,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after
            )
        elif len(self.requests) >= self.max_requests * 0.8:
            # Warning: approaching rate limit
            return RateLimitInfo(
                status=RateLimitStatus.WARNING,
                remaining=remaining,
                reset_time=current_time + self.time_window
            )
        else:
            # OK
            return RateLimitInfo(
                status=RateLimitStatus.OK,
                remaining=remaining,
                reset_time=current_time + self.time_window
            )
    
    def record_request(self) -> None:
        """Record a new request"""
        current_time = time.time()
        self.requests.append(current_time)
    
    async def wait_if_needed(self) -> None:
        """Wait if rate limit is exceeded"""
        rate_info = self.check_rate_limit()
        
        if rate_info.status == RateLimitStatus.EXCEEDED:
            if rate_info.retry_after:
                wait_time = min(rate_info.retry_after, self.max_backoff)
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.record_request()


# Global rate limiters for different APIs
api_rate_limiters = {
    'duck': RateLimiter(max_requests=100, time_window=3600),  # 100 requests per hour
    'dog': RateLimiter(max_requests=1000, time_window=3600),   # 1000 requests per hour
    'cat': RateLimiter(max_requests=10, time_window=60),       # 10 requests per minute
}


async def check_api_rate_limit(api_name: str) -> RateLimitInfo:
    """Check rate limit for a specific API"""
    if api_name not in api_rate_limiters:
        return RateLimitInfo(
            status=RateLimitStatus.OK,
            remaining=999,
            reset_time=time.time() + 3600
        )
    
    return api_rate_limiters[api_name].check_rate_limit()


async def wait_for_rate_limit(api_name: str) -> None:
    """Wait for rate limit if needed"""
    if api_name in api_rate_limiters:
        await api_rate_limiters[api_name].wait_if_needed()
