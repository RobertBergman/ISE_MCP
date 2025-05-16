import json
import logging
import os
import requests
import asyncio
from typing import Dict, Any, Optional
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

if not ISE_BASE or not USERNAME or not PASSWORD:
    logger.error("❌ Missing one or more required environment variables: ISE_BASE, USERNAME, PASSWORD")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ------------------------------- Load URLs -------------------------------

def load_urls(file_path='urls.json'):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ URLS file not found at {file_path}. Cannot register tools.")
        return []
    except json.JSONDecodeError:
        logger.error(f"❌ Error decoding JSON from {file_path}. Cannot register tools.")
        return []

URLS = load_urls()

# ------------------------------- FastMCP Server Setup -------------------------------

mcp = FastMCP(
    name="ISE MCP Server",
    instructions="Provides tools to fetch data from Cisco ISE. Tools may support filtering based on endpoint capabilities."
)
mcp.dependencies = [] # Explicitly add an empty list for dependencies

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
    def create_tool_function(current_api_url_path: str, InputModelType: type):
        # The `params` argument now has a default factory, creating an instance of InputModelType if not provided.
        def specific_tool_function(params: InputModelType = Field(default_factory=InputModelType)) -> dict:
            base_url = f"{ISE_BASE}{current_api_url_path}"
            params_for_request = {}

            # Access filter_expression if the model supports it (i.e., if it's FilterableToolInput)
            # and if params itself is not None (though default_factory should prevent params being None)
            if hasattr(params, 'filter_expression') and params.filter_expression is not None:
                params_for_request['filter'] = params.filter_expression

            # Access query_params (present in both models, but check if provided and params is not None)
            if params and params.query_params is not None:
                params_for_request.update(params.query_params)

            try:
                logger.info(f"🚀 Calling Cisco ISE API: {base_url} with params: {params_for_request}")
                response = requests.get(
                    base_url,
                    headers=HEADERS,
                    auth=(USERNAME, PASSWORD),
                    verify=False,
                    timeout=15,
                    params=params_for_request
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_err:
                error_message = f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}"
                logger.error(f"❌ {error_message}")
                raise ToolError(error_message) from http_err
            except requests.exceptions.RequestException as req_err:
                error_message = f"Request error occurred: {req_err}"
                logger.error(f"❌ {error_message}")
                raise ToolError(error_message) from req_err
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                logger.error(f"❌ {error_message}")
                raise ToolError(error_message) from e
        return specific_tool_function

    InputModel = FilterableToolInput if supports_filtering else NonFilterableToolInput
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
        await mcp.run_async() # Use run_async in async contexts

if __name__ == "__main__":
    asyncio.run(_main_async())
