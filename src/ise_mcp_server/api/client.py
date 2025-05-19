"""
API client for communicating with Cisco ISE with caching and rate limiting support.
"""
import httpx
import re
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple, Union
from fastmcp.exceptions import ToolError
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer
from aiolimiter import AsyncLimiter

from ..config.settings import (
    ISE_BASE, USERNAME, PASSWORD, ISE_VERIFY_SSL, HEADERS, logger,
    GLOBAL_RATE_LIMIT, RATE_LIMIT_ENABLED, CATEGORY_RATE_LIMITS, get_endpoint_category
)

class RateLimitExceededError(ToolError):
    """Exception raised when a rate limit is exceeded."""
    pass

class ISEApiClient:
    """
    Client for making requests to the Cisco ISE API with caching and rate limiting support.
    """
    
    # Default pagination settings for Cisco ISE API
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Default cache settings
    DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
    
    # Default backoff settings for rate limiting
    MIN_BACKOFF_TIME = 0.5  # seconds
    MAX_BACKOFF_TIME = 10.0  # seconds
    MAX_RETRIES = 3
    
    def __init__(self, cache_ttl=None, cache_enabled=True, rate_limit_enabled=None):
        """
        Initialize the ISE API client with caching and rate limiting support.
        
        Args:
            cache_ttl: Time-to-live for cached responses in seconds (default: 5 minutes)
            cache_enabled: Whether caching is enabled (default: True)
            rate_limit_enabled: Whether rate limiting is enabled (overrides settings)
        """
        # Ensure USERNAME and PASSWORD are not None
        assert USERNAME is not None, "USERNAME environment variable is not set."
        assert PASSWORD is not None, "PASSWORD environment variable is not set."
        self.auth = (USERNAME, PASSWORD)
        
        # Cache settings
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl if cache_ttl is not None else self.DEFAULT_CACHE_TTL
        
        # Initialize cache
        self.cache = Cache.MEMORY(namespace="ise_api")
        
        # Rate limiting settings
        self.rate_limit_enabled = RATE_LIMIT_ENABLED if rate_limit_enabled is None else rate_limit_enabled
        
        # Initialize rate limiters
        self.global_limiter = AsyncLimiter(GLOBAL_RATE_LIMIT, 1)  # tokens, time (in seconds)
        self.category_limiters = {
            category: AsyncLimiter(rate, 1)
            for category, rate in CATEGORY_RATE_LIMITS.items()
        }
        
        logger.info(f"📦 ISE API client initialized with:"
                   f"\n - Cache: {'enabled' if cache_enabled else 'disabled'}, TTL: {self.cache_ttl}s"
                   f"\n - Rate limiting: {'enabled' if self.rate_limit_enabled else 'disabled'}, "
                   f"Global: {GLOBAL_RATE_LIMIT}/sec")
    
    async def get(self, api_path: str, params: Optional[Dict[str, Any]] = None, 
                  auto_paginate: bool = True, use_cache: bool = None) -> Dict[str, Any]:
        """
        Make a GET request to the Cisco ISE API with caching and rate limiting.
        
        Args:
            api_path: The API endpoint path (relative to ISE_BASE)
            params: Optional query parameters
            auto_paginate: If True, automatically handle pagination and return all results
            use_cache: Whether to use cache for this request (overrides instance setting)
            
        Returns:
            The JSON response as a dictionary. If auto_paginate is True, the response will include
            all pages of data combined into a single response.
            
        Raises:
            ToolError: If an error occurs during the API request
            RateLimitExceededError: If rate limits are exceeded and cannot be handled
        """
        # Determine whether to use cache for this specific request
        should_use_cache = self.cache_enabled if use_cache is None else use_cache
        
        if auto_paginate:
            return await self._get_all_pages(api_path, params, use_cache=should_use_cache)
        
        base_url = f"{ISE_BASE}{api_path}"
        request_params = params or {}
        
        # Generate a cache key based on the URL and parameters
        cache_key = self._get_cache_key(base_url, request_params)
        
        # Try to get from cache first if caching is enabled
        if should_use_cache:
            cached_response = await self.cache.get(cache_key)
            if cached_response is not None:
                logger.info(f"🔄 Cache hit for: {base_url}")
                return json.loads(cached_response)
        
        # If not in cache or caching disabled, make the API request with rate limiting
        return await self._make_rate_limited_request(api_path, base_url, request_params, should_use_cache, cache_key)
    
    async def _make_rate_limited_request(self, api_path: str, base_url: str, 
                                         request_params: Dict[str, Any], 
                                         should_use_cache: bool, 
                                         cache_key: str) -> Dict[str, Any]:
        """
        Make a rate-limited API request with retries and backoff.
        
        Args:
            api_path: The API endpoint path
            base_url: The full URL for the request
            request_params: Query parameters
            should_use_cache: Whether to cache the response
            cache_key: The cache key for this request
            
        Returns:
            The API response as a dictionary
            
        Raises:
            ToolError: If an error occurs during the API request
            RateLimitExceededError: If rate limits are exceeded and cannot be handled
        """
        # Determine endpoint category for rate limiting
        category = get_endpoint_category(api_path)
        category_limiter = self.category_limiters.get(category, self.category_limiters["default"])
        
        retries = 0
        while retries <= self.MAX_RETRIES:
            try:
                # Apply rate limiting if enabled
                if self.rate_limit_enabled:
                    # First acquire the global limiter
                    async with self.global_limiter:
                        # Then acquire the category-specific limiter
                        async with category_limiter:
                            return await self._execute_request(
                                base_url, request_params, should_use_cache, cache_key
                            )
                else:
                    # No rate limiting, just make the request
                    return await self._execute_request(
                        base_url, request_params, should_use_cache, cache_key
                    )
            
            except RateLimitExceededError as e:
                # Calculate backoff time with exponential backoff
                backoff_time = min(
                    self.MIN_BACKOFF_TIME * (2 ** retries),
                    self.MAX_BACKOFF_TIME
                )
                
                if retries >= self.MAX_RETRIES:
                    logger.error(f"❌ Rate limit exceeded, max retries reached: {e}")
                    raise
                
                logger.warning(f"⚠️ Rate limit hit, backing off for {backoff_time:.2f}s "
                               f"(retry {retries+1}/{self.MAX_RETRIES})")
                await asyncio.sleep(backoff_time)
                retries += 1
            
            except Exception as e:
                # Don't retry other errors
                raise
    
    async def _execute_request(self, base_url: str, request_params: Dict[str, Any],
                               should_use_cache: bool, cache_key: str) -> Dict[str, Any]:
        """
        Execute the actual API request.
        
        Args:
            base_url: The full URL for the request
            request_params: Query parameters
            should_use_cache: Whether to cache the response
            cache_key: The cache key for this request
            
        Returns:
            The API response as a dictionary
            
        Raises:
            ToolError: If an error occurs during the API request
            RateLimitExceededError: If a rate limit is hit
        """
        try:
            logger.info(f"🚀 Calling Cisco ISE API (async): {base_url} with params: {request_params}")
            async with httpx.AsyncClient(auth=self.auth, verify=ISE_VERIFY_SSL, timeout=15) as client:
                response = await client.get(
                    base_url,
                    headers=HEADERS,
                    params=request_params
                )
                
                # Check for rate limiting response codes
                if response.status_code == 429:  # Too Many Requests
                    raise RateLimitExceededError(f"Rate limit exceeded: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                
                # Cache the result if caching is enabled
                if should_use_cache:
                    await self.cache.set(cache_key, json.dumps(result), ttl=self.cache_ttl)
                    logger.debug(f"💾 Cached response for: {base_url} (key: {cache_key})")
                
                return result
        except httpx.HTTPStatusError as http_err:
            # Check if this is a rate limit error
            if http_err.response.status_code == 429:
                raise RateLimitExceededError(f"Rate limit exceeded: {http_err.response.text}") from http_err
            
            error_message = f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}"
            logger.error(f"❌ {error_message}")
            raise ToolError(error_message) from http_err
        except httpx.RequestError as req_err:
            error_message = f"Request error occurred: {req_err}"
            logger.error(f"❌ {error_message}")
            raise ToolError(error_message) from req_err
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            logger.error(f"❌ {error_message}")
            raise ToolError(error_message) from e
    
    async def _get_all_pages(self, api_path: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch all pages of results for a given API endpoint with caching support.
        
        This method handles pagination automatically by fetching all pages and combining the results.
        Each page is cached individually to allow for efficient partial results reuse.
        
        Args:
            api_path: The API endpoint path
            params: Optional query parameters
            use_cache: Whether to use cache for this request
            
        Returns:
            Combined response with all paged results merged into a single response
        """
        # Initialize parameters for pagination
        request_params = params.copy() if params else {}
        
        # Ensure we use the maximum page size for efficiency
        if 'size' not in request_params:
            request_params['size'] = self.MAX_PAGE_SIZE
        
        # Get the first page
        page_num = 1  # Cisco ISE pagination starts at page 1
        request_params['page'] = page_num
        
        # Create a unique cache key for the paginated result set (without page parameter)
        base_url = f"{ISE_BASE}{api_path}"
        base_params = {k: v for k, v in request_params.items() if k != 'page'}
        pagination_cache_key = f"paginated:{self._get_cache_key(base_url, base_params)}"
        
        # Try to get the complete paginated result from cache
        if use_cache:
            cached_paginated_response = await self.cache.get(pagination_cache_key)
            if cached_paginated_response is not None:
                logger.info(f"🔄 Cache hit for paginated result: {api_path}")
                return json.loads(cached_paginated_response)
        
        # Get the first page (with caching)
        first_page_response = await self.get(api_path, request_params, auto_paginate=False, use_cache=use_cache)
        
        # Check if we need pagination (response has a 'SearchResult' key with 'total')
        if 'SearchResult' not in first_page_response or 'total' not in first_page_response['SearchResult']:
            # This endpoint doesn't seem to support pagination or has no results
            return first_page_response
        
        total_records = first_page_response['SearchResult']['total']
        page_size = int(request_params['size'])
        total_pages = (total_records + page_size - 1) // page_size  # Ceiling division
        
        # If only one page is needed, return the first page response
        if total_pages <= 1:
            return first_page_response
        
        # Initialize the combined result with the first page
        combined_result = first_page_response.copy()
        resources = first_page_response['SearchResult'].get('resources', [])
        
        # Fetch remaining pages
        for page in range(2, total_pages + 1):
            logger.info(f"📄 Fetching page {page} of {total_pages} for {api_path}")
            request_params['page'] = page
            try:
                page_response = await self.get(api_path, request_params, auto_paginate=False, use_cache=use_cache)
                page_resources = page_response['SearchResult'].get('resources', [])
                resources.extend(page_resources)
            except Exception as e:
                logger.error(f"❌ Error fetching page {page}: {e}")
                # Continue with the pages we've already fetched instead of failing completely
                break
        
        # Update the combined result with all resources
        combined_result['SearchResult']['resources'] = resources
        
        # Cache the complete paginated result
        if use_cache:
            await self.cache.set(pagination_cache_key, json.dumps(combined_result), ttl=self.cache_ttl)
            logger.debug(f"💾 Cached complete paginated result for: {api_path}")
        
        return combined_result
    
    async def get_stream(self, api_path: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream GET requests to the Cisco ISE API, yielding each page of results.
        
        This is useful for processing large result sets without loading everything into memory at once.
        Each page can be cached individually.
        
        Args:
            api_path: The API endpoint path (relative to ISE_BASE)
            params: Optional query parameters
            use_cache: Whether to use cache for this request
            
        Yields:
            Each page of results as a dictionary
            
        Raises:
            ToolError: If an error occurs during the API request
        """
        # Initialize parameters for pagination
        request_params = params.copy() if params else {}
        
        # Ensure we use the maximum page size for efficiency
        if 'size' not in request_params:
            request_params['size'] = self.MAX_PAGE_SIZE
        
        # Get the first page
        page_num = 1  # Cisco ISE pagination starts at page 1
        request_params['page'] = page_num
        
        first_page_response = await self.get(api_path, request_params, auto_paginate=False, use_cache=use_cache)
        yield first_page_response
        
        # Check if we need pagination (response has a 'SearchResult' key with 'total')
        if 'SearchResult' not in first_page_response or 'total' not in first_page_response['SearchResult']:
            # This endpoint doesn't seem to support pagination or has no results
            return
        
        total_records = first_page_response['SearchResult']['total']
        page_size = int(request_params['size'])
        total_pages = (total_records + page_size - 1) // page_size  # Ceiling division
        
        # If only one page is needed, we already yielded it
        if total_pages <= 1:
            return
        
        # Fetch and yield remaining pages
        for page in range(2, total_pages + 1):
            logger.info(f"📄 Streaming page {page} of {total_pages} for {api_path}")
            request_params['page'] = page
            try:
                page_response = await self.get(api_path, request_params, auto_paginate=False, use_cache=use_cache)
                yield page_response
            except Exception as e:
                logger.error(f"❌ Error fetching page {page}: {e}")
                # Stop iteration on error
                break
    
    def _get_cache_key(self, url: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for a request.
        
        Args:
            url: The full URL for the request
            params: The query parameters
            
        Returns:
            A string representing the cache key
        """
        # Sort params to ensure consistent key generation
        sorted_params = json.dumps(params, sort_keys=True) if params else "{}"
        return f"{url}:{sorted_params}"
    
    async def clear_cache(self, namespace: str = None) -> None:
        """
        Clear cache entries.
        
        Args:
            namespace: Optional namespace to clear (default: clear all cached entries)
        """
        logger.info(f"🧹 Clearing cache{' for namespace: ' + namespace if namespace else ''}")
        await self.cache.clear(namespace=namespace)
        
    async def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        This is primarily useful for debugging and monitoring.
        
        Returns:
            Dictionary with cache statistics
        """
        # Note: This implementation is specific to the memory cache.
        # For other cache types (Redis, etc.), this would need to be adapted.
        if hasattr(self.cache, '_cache'):
            cache_size = len(self.cache._cache)
            cache_keys = list(self.cache._cache.keys())
            cache_info = {
                "cache_type": "memory",
                "cache_size": cache_size,
                "cache_keys": cache_keys[:100] if len(cache_keys) > 100 else cache_keys,  # Limit number of keys returned
                "cache_ttl": self.cache_ttl,
                "cache_enabled": self.cache_enabled
            }
        else:
            cache_info = {
                "cache_type": type(self.cache).__name__,
                "cache_ttl": self.cache_ttl,
                "cache_enabled": self.cache_enabled,
                "note": "Detailed cache statistics not available for this cache type"
            }
        
        return cache_info
    
    async def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get information about the current rate limiting state.
        
        This is primarily useful for debugging and monitoring.
        
        Returns:
            Dictionary with rate limiting statistics
        """
        # Get global rate limiter info
        global_info = {
            "max_rate": self.global_limiter.max_rate,
            "time_period": self.global_limiter.time_period,
            "tokens_remaining": self.global_limiter._tokens  # Note: This is an internal attribute
        }
        
        # Get category rate limiter info
        category_info = {}
        for category, limiter in self.category_limiters.items():
            category_info[category] = {
                "max_rate": limiter.max_rate,
                "time_period": limiter.time_period,
                "tokens_remaining": limiter._tokens  # Note: This is an internal attribute
            }
        
        rate_limit_info = {
            "rate_limit_enabled": self.rate_limit_enabled,
            "global_limiter": global_info,
            "category_limiters": category_info,
            "backoff_settings": {
                "min_backoff_time": self.MIN_BACKOFF_TIME,
                "max_backoff_time": self.MAX_BACKOFF_TIME,
                "max_retries": self.MAX_RETRIES
            }
        }
        
        return rate_limit_info
    
    def configure_rate_limiting(self, enabled: Optional[bool] = None) -> Dict[str, Any]:
        """
        Configure rate limiting settings.
        
        Args:
            enabled: Whether rate limiting should be enabled
            
        Returns:
            Dictionary with the updated rate limiting configuration
        """
        if enabled is not None:
            self.rate_limit_enabled = enabled
            logger.info(f"🔄 Rate limiting {'enabled' if enabled else 'disabled'}")
        
        return {"rate_limit_enabled": self.rate_limit_enabled}