import os
import logging
from typing import Union, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ISEMCPServer")

# ISE Connection Settings
ISE_BASE = os.getenv("ISE_BASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ISE_VERIFY_SSL_STR = os.getenv("ISE_VERIFY_SSL", "true").lower()
ISE_VERIFY_SSL: Union[bool, str] = True

# Rate Limiting Settings
# Get rate limit values from environment variables with defaults
GLOBAL_RATE_LIMIT = int(os.getenv("ISE_GLOBAL_RATE_LIMIT", "30"))  # 30 requests/sec overall
RATE_LIMIT_ENABLED = os.getenv("ISE_RATE_LIMIT_ENABLED", "true").lower() == "true"

# Category-based rate limits
DEFAULT_CATEGORY_RATE_LIMIT = 10  # Default for unspecified categories

# Define rate limits for different endpoint categories
CATEGORY_RATE_LIMITS: Dict[str, int] = {
    # Authentication-related endpoints
    "auth": 5,
    # Device-related endpoints
    "device": 15,
    # Policy-related endpoints
    "policy": 8,
    # Default for other endpoints
    "default": DEFAULT_CATEGORY_RATE_LIMIT
}

# Endpoint category mappings based on URL patterns
ENDPOINT_CATEGORIES = [
    {"pattern": "/ers/config/identitygroup", "category": "auth"},
    {"pattern": "/ers/config/idstoresequence", "category": "auth"},
    {"pattern": "/ers/config/internaluser", "category": "auth"},
    {"pattern": "/ers/config/adminuser", "category": "auth"},
    {"pattern": "/ers/config/activedirectory", "category": "auth"},
    
    {"pattern": "/ers/config/networkdevice", "category": "device"},
    {"pattern": "/ers/config/endpoint", "category": "device"},
    {"pattern": "/ers/config/node", "category": "device"},
    {"pattern": "/ers/config/endpointgroup", "category": "device"},
    
    {"pattern": "/api/v1/policy", "category": "policy"},
    {"pattern": "/ers/config/authorizationprofile", "category": "policy"},
    {"pattern": "/ers/config/allowedprotocols", "category": "policy"},
    {"pattern": "/ers/config/sgacl", "category": "policy"},
    {"pattern": "/ers/config/sgt", "category": "policy"},
]

# Determine SSL verification setting
if ISE_VERIFY_SSL_STR == "false":
    ISE_VERIFY_SSL = False
    logger.warning("⚠️ SSL verification is DISABLED for Cisco ISE API calls. This is insecure and not recommended for production.")
elif ISE_VERIFY_SSL_STR == "true":
    ISE_VERIFY_SSL = True
else:
    # Path to CA bundle
    ISE_VERIFY_SSL = ISE_VERIFY_SSL_STR
    logger.info(f"ℹ️ Using CA bundle at {ISE_VERIFY_SSL} for Cisco ISE API SSL verification.")

# Validate critical settings
def validate_settings():
    """Validate that all required settings are present."""
    if not ISE_BASE or not USERNAME or not PASSWORD:
        logger.error("❌ Missing one or more required environment variables: ISE_BASE, USERNAME, PASSWORD. Exiting.")
        return False
    return True

# Common HTTP Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Server Settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_TRANSPORT = "streamable-http"

# Helper function to determine category for an API path
def get_endpoint_category(api_path: str) -> str:
    """
    Determine the category for a given API path.
    
    Args:
        api_path: The API endpoint path
        
    Returns:
        The category name (auth, device, policy, or default)
    """
    for mapping in ENDPOINT_CATEGORIES:
        if mapping["pattern"] in api_path:
            return mapping["category"]
    return "default"