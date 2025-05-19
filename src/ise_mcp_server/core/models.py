from typing import Dict, Any, Optional, List, Union, Literal
from pydantic import BaseModel, Field

class FilterableToolInput(BaseModel):
    """
    Input model for tools that support filtering on the ISE API.
    """
    filter_expression: Optional[str] = Field(
        default=None,
        description="Optional filter string for the API request (e.g., 'name.CONTAINS.somevalue')."
    )
    query_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary of additional query parameters. Supported parameters include:\n"
                    "- size: Number of results per page (default: 100, max: 100)\n"
                    "- page: Page number to fetch (default: 1, page numbering starts at 1)\n"
                    "- auto_paginate: Set to False to disable automatic pagination (default: True)\n"
                    "- use_cache: Set to False to bypass cache (default: True)\n"
                    "Example: {'size': 50, 'auto_paginate': False}"
    )

class NonFilterableToolInput(BaseModel):
    """
    Input model for tools that do not support filtering on the ISE API.
    """
    query_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary of additional query parameters. Supported parameters include:\n"
                    "- size: Number of results per page (default: 100, max: 100)\n"
                    "- page: Page number to fetch (default: 1, page numbering starts at 1)\n"
                    "- auto_paginate: Set to False to disable automatic pagination (default: True)\n"
                    "- use_cache: Set to False to bypass cache (default: True)\n"
                    "Example: {'size': 50, 'auto_paginate': False}"
    )
    
class CacheClearInput(BaseModel):
    """
    Input model for clearing the cache.
    """
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to clear. If not provided, all cached entries will be cleared."
    )

class CacheInfoInput(BaseModel):
    """
    Input model for getting cache information.
    """
    pass  # No parameters needed for cache info

class CacheConfigInput(BaseModel):
    """
    Input model for configuring cache settings.
    """
    enabled: Optional[bool] = Field(
        default=None,
        description="Whether caching should be enabled. If not provided, the current setting is retained."
    )
    ttl: Optional[int] = Field(
        default=None,
        description="Time-to-live for cached responses in seconds. If not provided, the current setting is retained."
    )

# Rate limiting models
class RateLimitCategory(BaseModel):
    """
    Model for a rate limit category definition.
    """
    pattern: str = Field(
        description="URL pattern to match for this category"
    )
    category: str = Field(
        description="Category name (e.g., 'auth', 'device', 'policy', etc.)"
    )

class RateLimitCategorySettings(BaseModel):
    """
    Model for rate limit settings for a specific category.
    """
    category: str = Field(
        description="Category name (e.g., 'auth', 'device', 'policy', 'default')"
    )
    rate: int = Field(
        description="Maximum number of requests per second for this category",
        gt=0
    )

class RateLimitSettings(BaseModel):
    """
    Model for global rate limiting settings.
    """
    enabled: bool = Field(
        default=True,
        description="Whether rate limiting is enabled"
    )
    global_rate_limit: int = Field(
        default=30,
        description="Global rate limit (requests per second)",
        gt=0
    )
    category_limits: List[RateLimitCategorySettings] = Field(
        default_factory=list,
        description="Rate limits for specific categories"
    )
    endpoint_categories: List[RateLimitCategory] = Field(
        default_factory=list,
        description="Endpoint category definitions based on URL patterns"
    )
    
class RateLimitConfigInput(BaseModel):
    """
    Input model for configuring rate limiting settings.
    """
    enabled: Optional[bool] = Field(
        default=None,
        description="Whether rate limiting should be enabled. If not provided, the current setting is retained."
    )
    global_rate_limit: Optional[int] = Field(
        default=None,
        description="Global rate limit (requests per second). If not provided, the current setting is retained.",
        gt=0
    )
    category_rate_limit: Optional[Dict[str, int]] = Field(
        default=None,
        description="Dictionary of category-specific rate limits. Example: {'auth': 5, 'device': 15}. If not provided, the current settings are retained."
    )

class RateLimitInfoInput(BaseModel):
    """
    Input model for getting rate limiting information.
    """
    pass  # No parameters needed for rate limit info