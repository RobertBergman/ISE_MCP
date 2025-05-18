import json
import logging
import os
import httpx # Changed from requests
import asyncio
import sys # Added for sys.exit
from typing import Dict, Any, Optional, Type, Union # Added Union for type hinting
from pathlib import Path # Add this import
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ISEMCPServer")

ISE_BASE = os.getenv("ISE_BASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ISE_VERIFY_SSL_STR = os.getenv("ISE_VERIFY_SSL", "true").lower()
ISE_VERIFY_SSL: Union[bool, str] = True # Initialize and type hint

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


if not ISE_BASE or not USERNAME or not PASSWORD:
    logger.error("❌ Missing one or more required environment variables: ISE_BASE, USERNAME, PASSWORD. Exiting.")
    sys.exit(1) # Exit if critical env vars are missing
else:
    # Ensure USERNAME and PASSWORD are not None for httpx auth
    assert USERNAME is not None, "USERNAME environment variable is not set."
    assert PASSWORD is not None, "PASSWORD environment variable is not set."
    # auth_tuple is defined here, after asserts ensure USERNAME and PASSWORD are not None
    # This helps Mypy understand they are strings for the httpx.AsyncClient call.
    auth_tuple = (USERNAME, PASSWORD)


HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ------------------------------- Load URLs -------------------------------

def load_urls(file_name='urls.json'): # Changed default to just file_name
    # Get the directory of the current script
    script_dir = Path(__file__).resolve().parent
    # Construct the full path to the urls.json file
    file_path = script_dir / file_name
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ URLS file not found at {file_path}. Cannot register tools.")
        return []
    except json.JSONDecodeError:
        logger.error(f"❌ Error decoding JSON from {file_path}. Cannot register tools.")
        return []

URLS = load_urls() # This will now use the more robust path

# ------------------------------- FastMCP Server Setup -------------------------------

mcp: FastMCP = FastMCP( # Added type hint for mcp
    name="ISE MCP Server",
    instructions="Provides tools to fetch data from Cisco ISE. Tools may support filtering based on endpoint capabilities."
)
mcp.dependencies = [] # Re-added this line for fastmcp dev compatibility

# ------------------------------- Input Schemas for Tools -------------------------------

class FilterableToolInput(BaseModel):
    filter_expression: Optional[str] = Field(
        default=None,
        description="Optional filter string for the API request (e.g., 'name.CONTAINS.somevalue')."
    )
    query_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary of additional query parameters (e.g., {'size': 10, 'page': 1})."
    )

class NonFilterableToolInput(BaseModel):
    query_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary of additional query parameters (e.g., {'size': 10, 'page': 1})."
    )

# ------------------------------- Dynamic Tool Registration -------------------------------

for entry in URLS:
    tool_name = entry.get("Name", "").replace(" ", "_").lower()
    api_url_path = entry.get("URL")
    filterable_fields = entry.get("FilterableFields", [])

    if not tool_name or not api_url_path:
        logger.warning(f"⚠️ Skipping entry due to missing 'Name' or 'URL': {entry}")
        continue

    # Determine if the endpoint supports filtering
    supports_filtering = bool(filterable_fields)

    # Define the tool function
    def create_tool_function(current_api_url_path: str, InputModelType: Type[BaseModel]): # Hinted InputModelType
        # The `params` argument now has a default factory, creating an instance of InputModelType if not provided.
        async def specific_tool_function(params: InputModelType = Field(default_factory=InputModelType)) -> dict: # type: ignore[valid-type] # Made async & ignored Mypy error
            base_url = f"{ISE_BASE}{current_api_url_path}"
            request_params = {} # Renamed to avoid conflict with 'params' argument

            # Access filter_expression if the model supports it
            if hasattr(params, 'filter_expression') and params.filter_expression is not None: # type: ignore[attr-defined]
                request_params['filter'] = params.filter_expression # type: ignore[attr-defined]

            # Access query_params
            if params and hasattr(params, 'query_params') and params.query_params is not None: # type: ignore[attr-defined]
                request_params.update(params.query_params) # type: ignore[attr-defined]

            try:
                logger.info(f"🚀 Calling Cisco ISE API (async): {base_url} with params: {request_params}")
                # auth_tuple is defined in the outer scope after asserts
                async with httpx.AsyncClient(auth=auth_tuple, verify=ISE_VERIFY_SSL, timeout=15) as client:
                    response = await client.get(
                        base_url,
                        headers=HEADERS,
                        params=request_params
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as http_err:
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
        return specific_tool_function

    InputModel: Type[BaseModel] = FilterableToolInput if supports_filtering else NonFilterableToolInput # Hinted InputModel
    tool_func_instance = create_tool_function(api_url_path, InputModel)

    # Set tool name and description
    tool_func_instance.__name__ = tool_name
    description = f"Fetch data for {entry['Name']} from Cisco ISE (Endpoint: {api_url_path})."
    if supports_filtering:
        description += f" Supports filtering on fields: {', '.join(filterable_fields)}."
    else:
        description += " Does not support filtering."
    tool_func_instance.__doc__ = description

    # Register the tool. FastMCP will infer the schema from the function's type hints.
    mcp.add_tool(tool_func_instance)
    logger.info(f"✅ Registered tool: {tool_name} for URL: {api_url_path} with input model: {InputModel.__name__}")

# ------------------------------- Entry Point -------------------------------

async def _main_async():
    if not URLS:
        logger.error("No tools were registered. Check urls.json and logs. Exiting.")
    else:
        try:
            # get_tools() is async according to documentation examples
            tools_dict = await mcp.get_tools()
            num_tools = len(tools_dict)
            logger.info(f"🚀 Starting ISE FastMCP Server with {num_tools} tools...")
        except Exception as e:
            logger.error(f"Failed to get tool count: {e}. Starting server anyway.")
            # Fallback message if getting tool count fails
            logger.info(f"🚀 Starting ISE FastMCP Server...")
        await mcp.run_async(transport="streamable-http", host="127.0.0.1", port=8000) # Use streamable-http transport

if __name__ == "__main__":
    asyncio.run(_main_async())
