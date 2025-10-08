"""
CMS API Client Abstractions

Abstract HTTP clients and authentication managers for CMS provider integrations.
Enables managed CMS services including content migration, bulk operations,
and programmatic content management across different CMS platforms.

Key Components:
- CMSAPIClient: Abstract base for all CMS API clients
- Authentication managers for different auth methods
- Request/response abstractions with error handling
- Rate limiting and connection pooling
- Provider-specific client implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from pydantic import BaseModel, ConfigDict, Field
import aiohttp
import asyncio
import json
import time
from datetime import datetime, timedelta
from enum import Enum
import logging

from .models import (
    ContentItem, ContentCollection, ContentType, MediaAsset,
    Author, CMSQuery, CMSWebhook, ContentStatus
)
from .base_provider import CMSAuthMethod


class APIError(Exception):
    """Base exception for CMS API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message)


class AuthenticationError(APIError):
    """Authentication-related API error"""
    pass


class RateLimitError(APIError):
    """Rate limiting error"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(APIError):
    """Content validation error"""
    pass


class HTTPMethod(str, Enum):
    """HTTP methods for API requests"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class APIRequest(BaseModel):
    """API request configuration"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    method: HTTPMethod = Field(..., description="HTTP method")
    url: str = Field(..., description="Request URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    data: Optional[Dict[str, Any]] = Field(None, description="Request body data")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retries: int = Field(default=3, description="Number of retry attempts")


class APIResponse(BaseModel):
    """API response wrapper"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    raw_response: Optional[str] = Field(None, description="Raw response text")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    execution_time: float = Field(..., description="Request execution time in seconds")


class AuthenticationManager(ABC):
    """Abstract authentication manager for CMS providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._token_cache: Dict[str, Any] = {}
        self._token_expires: Optional[datetime] = None

    @abstractmethod
    async def authenticate(self) -> Dict[str, str]:
        """
        Perform authentication and return headers for API requests.

        Returns:
            Dictionary of authentication headers
        """
        pass

    @abstractmethod
    async def refresh_token(self) -> bool:
        """
        Refresh authentication token if supported.

        Returns:
            True if token was refreshed successfully
        """
        pass

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get current authentication headers, refreshing if needed"""
        if self._needs_refresh():
            await self.refresh_token()

        return await self.authenticate()

    def _needs_refresh(self) -> bool:
        """Check if authentication needs to be refreshed"""
        if not self._token_expires:
            return False

        # Refresh 5 minutes before expiry
        return datetime.utcnow() + timedelta(minutes=5) >= self._token_expires

    def clear_cache(self) -> None:
        """Clear cached authentication data"""
        self._token_cache.clear()
        self._token_expires = None


class APIKeyAuthManager(AuthenticationManager):
    """API key authentication manager"""

    async def authenticate(self) -> Dict[str, str]:
        """Authenticate using API key"""
        api_key = self.config.get("api_key")
        if not api_key:
            raise AuthenticationError("API key not provided")

        # Different providers use different header formats
        auth_header = self.config.get("auth_header", "Authorization")
        auth_format = self.config.get("auth_format", "Bearer {}")

        return {
            auth_header: auth_format.format(api_key)
        }

    async def refresh_token(self) -> bool:
        """API keys don't need refreshing"""
        return True


class OAuthManager(AuthenticationManager):
    """OAuth authentication manager"""

    async def authenticate(self) -> Dict[str, str]:
        """Authenticate using OAuth token"""
        if not self._token_cache.get("access_token"):
            await self._obtain_token()

        access_token = self._token_cache.get("access_token")
        if not access_token:
            raise AuthenticationError("Failed to obtain OAuth token")

        return {
            "Authorization": f"Bearer {access_token}"
        }

    async def refresh_token(self) -> bool:
        """Refresh OAuth token using refresh token"""
        refresh_token = self._token_cache.get("refresh_token")
        if not refresh_token:
            return False

        try:
            # This would implement provider-specific OAuth refresh
            # For now, just clear cache to force re-authentication
            self.clear_cache()
            return True
        except Exception:
            return False

    async def _obtain_token(self) -> None:
        """Obtain initial OAuth token"""
        # This would implement the OAuth flow for each provider
        # For now, assume token is provided in config
        token = self.config.get("access_token")
        if token:
            self._token_cache["access_token"] = token

            # Set expiry if provided
            expires_in = self.config.get("expires_in", 3600)
            self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in)


class JWTAuthManager(AuthenticationManager):
    """JWT token authentication manager"""

    async def authenticate(self) -> Dict[str, str]:
        """Authenticate using JWT token"""
        jwt_token = self.config.get("jwt_token")
        if not jwt_token:
            jwt_token = await self._generate_jwt()

        if not jwt_token:
            raise AuthenticationError("JWT token not available")

        return {
            "Authorization": f"Bearer {jwt_token}"
        }

    async def refresh_token(self) -> bool:
        """Generate new JWT token"""
        try:
            new_token = await self._generate_jwt()
            if new_token:
                self.config["jwt_token"] = new_token
                return True
        except Exception:
            pass
        return False

    async def _generate_jwt(self) -> Optional[str]:
        """Generate JWT token using provider-specific method"""
        # This would implement JWT generation for each provider
        # For now, return configured token
        return self.config.get("jwt_token")


class RateLimiter:
    """Rate limiting for API requests"""

    def __init__(self, requests_per_second: float = 10, burst_limit: int = 50):
        self.requests_per_second = requests_per_second
        self.burst_limit = burst_limit
        self._tokens = burst_limit
        self._last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request"""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_update

            # Add tokens based on elapsed time
            self._tokens = min(
                self.burst_limit,
                self._tokens + elapsed * self.requests_per_second
            )
            self._last_update = now

            if self._tokens < 1:
                # Wait until we have a token
                wait_time = (1 - self._tokens) / self.requests_per_second
                await asyncio.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= 1


class CMSAPIClient(ABC):
    """Abstract base class for CMS API clients"""

    def __init__(self, provider_name: str, config: Dict[str, Any]):
        self.provider_name = provider_name
        self.config = config

        # Initialize authentication manager
        self.auth_manager = self._create_auth_manager()

        # Initialize rate limiter
        rate_limit = config.get("rate_limit", 10)  # requests per second
        self.rate_limiter = RateLimiter(rate_limit)

        # HTTP session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None

        # Request tracking
        self._request_count = 0
        self._error_count = 0

    @abstractmethod
    def _create_auth_manager(self) -> AuthenticationManager:
        """Create appropriate authentication manager for this provider"""
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """Get base URL for this CMS provider's API"""
        pass

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure HTTP session is created"""
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.config.get("timeout", 30))
            connector = aiohttp.TCPConnector(
                limit=self.config.get("connection_limit", 100),
                ttl_dns_cache=300,
                use_dns_cache=True
            )

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": f"CMS-Client/{self.provider_name}"}
            )

    async def close(self) -> None:
        """Close HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None

    async def _make_request(self, request: APIRequest) -> APIResponse:
        """Make HTTP request with authentication, rate limiting, and error handling"""
        await self._ensure_session()
        await self.rate_limiter.acquire()

        # Get authentication headers
        auth_headers = await self.auth_manager.get_auth_headers()
        request.headers.update(auth_headers)

        # Add provider-specific headers
        request.headers.update(self._get_default_headers())

        start_time = time.time()
        last_exception = None

        for attempt in range(request.retries + 1):
            try:
                self._request_count += 1

                async with self._session.request(
                    method=request.method.value,
                    url=request.url,
                    headers=request.headers,
                    params=request.params,
                    json=request.data,
                    timeout=request.timeout
                ) as response:

                    execution_time = time.time() - start_time
                    response_text = await response.text()

                    # Handle different response types
                    try:
                        response_data = await response.json()
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        response_data = {"raw_text": response_text}

                    api_response = APIResponse(
                        status_code=response.status,
                        headers=dict(response.headers),
                        data=response_data,
                        raw_response=response_text,
                        execution_time=execution_time
                    )

                    # Handle error responses
                    if response.status >= 400:
                        await self._handle_error_response(api_response)

                    return api_response

            except aiohttp.ClientError as e:
                last_exception = e
                self._error_count += 1

                if attempt < request.retries:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                    await asyncio.sleep(wait_time)
                    continue

                # Final attempt failed
                raise APIError(f"Request failed after {request.retries + 1} attempts: {str(e)}")

        # Should not reach here, but just in case
        raise APIError(f"Request failed: {str(last_exception)}")

    async def _handle_error_response(self, response: APIResponse) -> None:
        """Handle HTTP error responses"""
        status_code = response.status_code
        error_data = response.data

        if status_code == 401:
            # Clear auth cache and retry once
            self.auth_manager.clear_cache()
            raise AuthenticationError("Authentication failed", status_code, error_data)

        elif status_code == 429:
            # Rate limiting
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else 60
            raise RateLimitError(
                f"Rate limit exceeded, retry after {retry_seconds} seconds",
                retry_seconds
            )

        elif status_code in [400, 422]:
            # Validation errors
            error_message = error_data.get("message", "Validation error")
            raise ValidationError(error_message, status_code, error_data)

        else:
            # Generic API error
            error_message = error_data.get("message", f"API error: {status_code}")
            raise APIError(error_message, status_code, error_data)

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for this provider"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    # Abstract methods for content operations
    @abstractmethod
    async def get_content_types(self) -> List[ContentType]:
        """Get all content types/collections from the CMS"""
        pass

    @abstractmethod
    async def get_content(self, query: CMSQuery) -> ContentCollection:
        """Get content items based on query parameters"""
        pass

    @abstractmethod
    async def get_content_item(self, content_type: str, item_id: str) -> ContentItem:
        """Get a specific content item by ID"""
        pass

    @abstractmethod
    async def create_content(self, content: ContentItem) -> ContentItem:
        """Create new content item"""
        pass

    @abstractmethod
    async def update_content(self, content: ContentItem) -> ContentItem:
        """Update existing content item"""
        pass

    @abstractmethod
    async def delete_content(self, content_type: str, item_id: str) -> bool:
        """Delete content item"""
        pass

    @abstractmethod
    async def upload_media(self, file_path: str, metadata: Dict[str, Any]) -> MediaAsset:
        """Upload media asset"""
        pass

    @abstractmethod
    async def get_media_assets(self, folder: Optional[str] = None) -> List[MediaAsset]:
        """Get media assets"""
        pass

    # Bulk operations for managed services
    async def bulk_create_content(self, content_items: List[ContentItem]) -> List[ContentItem]:
        """Create multiple content items"""
        results = []
        for item in content_items:
            try:
                created_item = await self.create_content(item)
                results.append(created_item)
            except Exception as e:
                logging.error(f"Failed to create content item {item.id}: {e}")
                # Continue with other items
        return results

    async def bulk_update_content(self, content_items: List[ContentItem]) -> List[ContentItem]:
        """Update multiple content items"""
        results = []
        for item in content_items:
            try:
                updated_item = await self.update_content(item)
                results.append(updated_item)
            except Exception as e:
                logging.error(f"Failed to update content item {item.id}: {e}")
        return results

    async def export_all_content(self) -> Dict[str, List[ContentItem]]:
        """Export all content from the CMS (for backups/migration)"""
        content_types = await self.get_content_types()
        all_content = {}

        for content_type in content_types:
            query = CMSQuery(
                content_type=content_type.name,
                per_page=100,  # Large page size for bulk export
                include_drafts=True
            )

            all_items = []
            page = 1

            while True:
                query.page = page
                collection = await self.get_content(query)
                all_items.extend(collection.items)

                if not collection.has_more:
                    break

                page += 1

            all_content[content_type.name] = all_items

        return all_content

    # Utility methods
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "provider": self.provider_name,
            "requests_made": self._request_count,
            "errors_encountered": self._error_count,
            "error_rate": self._error_count / max(1, self._request_count),
            "session_active": self._session is not None
        }


# Factory for creating authentication managers
class AuthManagerFactory:
    """Factory for creating authentication managers"""

    @staticmethod
    def create_auth_manager(auth_method: CMSAuthMethod, config: Dict[str, Any]) -> AuthenticationManager:
        """Create appropriate authentication manager"""
        if auth_method == CMSAuthMethod.API_KEY:
            return APIKeyAuthManager(config)
        elif auth_method in [CMSAuthMethod.GITHUB_OAUTH, CMSAuthMethod.OAUTH2]:
            return OAuthManager(config)
        elif auth_method == CMSAuthMethod.JWT:
            return JWTAuthManager(config)
        else:
            raise ValueError(f"Unsupported authentication method: {auth_method}")


# Export key classes
__all__ = [
    "CMSAPIClient", "AuthenticationManager", "APIKeyAuthManager",
    "OAuthManager", "JWTAuthManager", "AuthManagerFactory",
    "APIRequest", "APIResponse", "RateLimiter",
    "APIError", "AuthenticationError", "RateLimitError", "ValidationError"
]