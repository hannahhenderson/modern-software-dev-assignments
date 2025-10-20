"""
Health check utilities for monitoring server status.
"""

import time
import asyncio
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    status: HealthStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class HealthChecker:
    """Health checker for external APIs"""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.api_endpoints = {
            'duck': 'https://random-d.uk/api/v2/random',
            'dog': 'https://random.dog/woof.json',
            'cat': 'https://api.thecatapi.com/v1/images/search'
        }
    
    async def check_api_health(self, api_name: str) -> HealthCheckResult:
        """Check health of a specific API"""
        if api_name not in self.api_endpoints:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Unknown API: {api_name}",
                details={"api": api_name, "error": "Unknown API"}
            )
        
        endpoint = self.api_endpoints[api_name]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, timeout=self.timeout)
                
                if response.status_code == 200:
                    return HealthCheckResult(
                        status=HealthStatus.HEALTHY,
                        message=f"{api_name} API is healthy",
                        details={"api": api_name, "status_code": 200, "response_time": response.elapsed.total_seconds()}
                    )
                elif response.status_code == 429:
                    return HealthCheckResult(
                        status=HealthStatus.DEGRADED,
                        message=f"{api_name} API is rate limited",
                        details={"api": api_name, "status_code": 429, "rate_limited": True}
                    )
                else:
                    return HealthCheckResult(
                        status=HealthStatus.DEGRADED,
                        message=f"{api_name} API returned status {response.status_code}",
                        details={"api": api_name, "status_code": response.status_code}
                    )
        
        except httpx.TimeoutException:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{api_name} API timeout",
                details={"api": api_name, "error": "timeout", "timeout_seconds": self.timeout}
            )
        
        except httpx.ConnectError:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{api_name} API connection failed",
                details={"api": api_name, "error": "connection_failed"}
            )
        
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"{api_name} API error: {str(e)}",
                details={"api": api_name, "error": str(e)}
            )
    
    async def check_all_apis(self) -> Dict[str, HealthCheckResult]:
        """Check health of all APIs"""
        results = {}
        
        for api_name in self.api_endpoints:
            results[api_name] = await self.check_api_health(api_name)
        
        return results
    
    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Get overall health status from individual results"""
        if not results:
            return HealthStatus.UNHEALTHY
        
        statuses = [result.status for result in results.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED


# Global health checker instance
health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    api_results = await health_checker.check_all_apis()
    overall_status = health_checker.get_overall_status(api_results)
    
    return {
        "status": overall_status.value,
        "timestamp": time.time(),
        "apis": {
            api_name: {
                "status": result.status.value,
                "message": result.message,
                "details": result.details
            }
            for api_name, result in api_results.items()
        },
        "summary": {
            "total_apis": len(api_results),
            "healthy": sum(1 for r in api_results.values() if r.status == HealthStatus.HEALTHY),
            "degraded": sum(1 for r in api_results.values() if r.status == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for r in api_results.values() if r.status == HealthStatus.UNHEALTHY)
        }
    }
