"""
Enhanced error handling with specific error types and user-friendly messages.
"""

import httpx
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass


class ErrorType(Enum):
    """Types of errors that can occur"""
    NETWORK_TIMEOUT = "network_timeout"
    HTTP_ERROR = "http_error"
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN = "unknown"


@dataclass
class APIError:
    """Structured API error information"""
    error_type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    user_friendly: bool = True


class PettingZooError(Exception):
    """Base exception for Petting Zootopia errors"""
    
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class NetworkError(PettingZooError):
    """Network-related error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.NETWORK_TIMEOUT, details)


class RateLimitError(PettingZooError):
    """Rate limit exceeded error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.RATE_LIMIT, details)


class APIError(PettingZooError):
    """External API error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.API_ERROR, details)


class ValidationError(PettingZooError):
    """Input validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.VALIDATION_ERROR, details)


def handle_httpx_error(error: httpx.HTTPError, api_name: str) -> PettingZooError:
    """Convert httpx errors to our custom errors with user-friendly messages"""
    
    if isinstance(error, httpx.TimeoutException):
        return NetworkError(
            message=f"The {api_name} API is taking too long to respond. Please try again in a moment.",
            details={"api": api_name, "timeout": True}
        )
    
    elif isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        
        if status_code == 429:  # Rate limit
            return RateLimitError(
                message=f"The {api_name} API is currently busy. Please wait a moment before trying again.",
                details={"api": api_name, "status_code": status_code}
            )
        
        elif 400 <= status_code < 500:  # Client error
            return APIError(
                message=f"The {api_name} API is having issues. Please try again later.",
                details={"api": api_name, "status_code": status_code}
            )
        
        elif 500 <= status_code < 600:  # Server error
            return APIError(
                message=f"The {api_name} API is temporarily unavailable. Please try again later.",
                details={"api": api_name, "status_code": status_code}
            )
        
        else:
            return APIError(
                message=f"Unexpected response from {api_name} API. Please try again.",
                details={"api": api_name, "status_code": status_code}
            )
    
    elif isinstance(error, httpx.ConnectError):
        return NetworkError(
            message=f"Unable to connect to {api_name} API. Please check your internet connection.",
            details={"api": api_name, "connection_error": True}
        )
    
    else:
        return NetworkError(
            message=f"Network error while contacting {api_name} API. Please try again.",
            details={"api": api_name, "error": str(error)}
        )


def get_user_friendly_message(error: PettingZooError, animal: str) -> str:
    """Get a user-friendly error message for the web interface"""
    
    if error.error_type == ErrorType.RATE_LIMIT:
        return f"🐾 The {animal} API is busy right now. The animals are taking a break! Please try again in a moment."
    
    elif error.error_type == ErrorType.NETWORK_TIMEOUT:
        return f"🐾 The {animal}s are being shy and taking their time. Please try again!"
    
    elif error.error_type == ErrorType.API_ERROR:
        return f"🐾 The {animal} API is having a nap. Please try again later!"
    
    elif error.error_type == ErrorType.VALIDATION_ERROR:
        return f"🐾 That doesn't look like a valid {animal} request. Please try again!"
    
    else:
        return f"🐾 The {animal}s are all sleeping right now. Please try again later!"


def get_sad_animal_url(animal: str) -> str:
    """Get URL for sad animal image based on animal type"""
    sad_animals = {
        "duck": "https://i.pinimg.com/736x/c2/16/df/c216df7a2af5dc737c9b2041ef295835.jpg",
        "dog": "https://whitworthpetvet.com/wp-content/uploads/2016/07/sad-dog.jpg",
        "cat": "https://people.com/thmb/aaQtgLVy5cJkYUSEQbpOlgWm5-4=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():focal(899x0:901x2):format(webp)/21042210_264995290674140_8840525631411191808_n-530848c0d1134a31bc03861ea9ddd700.jpg"
    }
    return sad_animals.get(animal, sad_animals["dog"])  # Default to sad dog


def validate_input(name: str) -> None:
    """Validate input parameters"""
    if not name or not isinstance(name, str):
        raise ValidationError("Name must be a non-empty string")
    
    if len(name) > 100:
        raise ValidationError("Name must be 100 characters or less")
    
    if not name.strip():
        raise ValidationError("Name cannot be just whitespace")
