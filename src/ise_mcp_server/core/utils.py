"""
Utility functions for the ISE MCP server.
"""
from typing import Dict, Any

def process_filter_expression(filter_expression: str) -> Dict[str, str]:
    """
    Process a filter expression and convert it to query parameters.
    
    Args:
        filter_expression: A string in the format "field.OPERATION.value"
        
    Returns:
        A dictionary with the filter parameter.
    """
    return {"filter": filter_expression}

def sanitize_tool_name(name: str) -> str:
    """
    Convert a human-readable name to a valid tool name.
    
    Args:
        name: Human-readable name (e.g., "Identity Groups")
        
    Returns:
        A valid tool name (e.g., "identity_groups")
    """
    return name.replace(" ", "_").lower()

def generate_tool_docstring(name: str, api_url_path: str, filterable_fields: list = None) -> str:
    """
    Generate a docstring for a tool based on its metadata.
    
    Args:
        name: Human-readable name of the tool
        api_url_path: The API endpoint path
        filterable_fields: List of fields that can be used for filtering
        
    Returns:
        A docstring for the tool
    """
    description = f"Fetch data for {name} from Cisco ISE (Endpoint: {api_url_path})."
    
    if filterable_fields and len(filterable_fields) > 0:
        description += f" Supports filtering on fields: {', '.join(filterable_fields)}."
    else:
        description += " Does not support filtering."
    
    # Add pagination information
    description += "\n\nPagination: This tool automatically handles pagination, combining all result pages "
    description += "into a single response. You can control pagination with the 'query_params' parameter:\n"
    description += "- Set 'size' to control results per page (default 100, max 100)\n"
    description += "- Set 'auto_paginate' to False to disable automatic pagination and only get the first page\n"
    description += "- Explicitly set 'page' if you want a specific page when auto_paginate is False"
        
    return description