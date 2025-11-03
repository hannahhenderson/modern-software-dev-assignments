"""
Industry-standard rate limiting using pyrate-limiter.
Replaces custom implementation with battle-tested library.
"""

import logging
from typing import Optional
from pyrate_limiter import Limiter, RequestRate, Duration
from pyrate_limiter.exceptions import RateLimitExceeded

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class APIRateLimiter:
    """Industry-standard rate limiter using pyrate-limiter"""
    
    def __init__(self):
        # Define rate limits per API based on their actual limits
        self.limiters = {
            'duck': Limiter(RequestRate(100, Duration.HOUR)),  # 100/hour (conservative)
            'dog': Limiter(RequestRate(1000, Duration.HOUR)),  # 1000/hour (generous)
            'cat': Limiter(RequestRate(10, Duration.MINUTE)),  # 10/minute (matches API limit)
        }
    
    async def check_rate_limit(self, api_name: str, user_id: str = "default") -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            api_name: Name of the API (duck, dog, cat)
            user_id: User identifier for rate limiting
            
        Returns:
            True if request is allowed, False if rate limited
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        if api_name not in self.limiters:
            logger.warning(f"No rate limiter configured for API: {api_name}")
            return True
        
        try:
            # Use API name + user_id as the key for rate limiting
            key = f"{api_name}:{user_id}"
            self.limiters[api_name].try_acquire(key)
            logger.debug(f"Rate limit check passed for {key}")
            return True
            
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded for {api_name}: {e}")
            raise RateLimitError(f"Rate limit exceeded for {api_name} API. Please try again later.")
    
    def get_rate_limit_info(self, api_name: str, user_id: str = "default") -> dict:
        """
        Get rate limit information for an API.
        
        Args:
            api_name: Name of the API
            user_id: User identifier
            
        Returns:
            Dictionary with rate limit information
        """
        if api_name not in self.limiters:
            return {
                "api": api_name,
                "limit": "unlimited",
                "remaining": "unlimited",
                "reset_time": None
            }
        
        # Get bucket info from the limiter
        key = f"{api_name}:{user_id}"
        bucket = self.limiters[api_name].get_bucket(key)
        
        if bucket:
            return {
                "api": api_name,
                "limit": bucket.rate.limit,
                "remaining": bucket.remaining,
                "reset_time": bucket.reset_time,
                "window": bucket.rate.interval
            }
        else:
            return {
                "api": api_name,
                "limit": "unknown",
                "remaining": "unknown",
                "reset_time": None
            }


# Global rate limiter instance
rate_limiter = APIRateLimiter()


async def check_api_rate_limit(api_name: str, user_id: str = "default") -> bool:
    """
    Convenience function to check rate limit for an API.
    
    Args:
        api_name: Name of the API (duck, dog, cat)
        user_id: User identifier for rate limiting
        
    Returns:
        True if request is allowed
        
    Raises:
        RateLimitError: If rate limit is exceeded
    """
    return await rate_limiter.check_rate_limit(api_name, user_id)


def get_rate_limit_info(api_name: str, user_id: str = "default") -> dict:
    """
    Get rate limit information for an API.
    
    Args:
        api_name: Name of the API
        user_id: User identifier
        
    Returns:
        Dictionary with rate limit information
    """
    return rate_limiter.get_rate_limit_info(api_name, user_id)
