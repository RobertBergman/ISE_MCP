# ISE MCP Server (using FastMCP)

## Overview

The ISE MCP Server is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server built with the Python [`fastmcp`](https://gofastmcp.com/) library. It dynamically exposes Cisco Identity Services Engine (ISE) API endpoints as structured, discoverable MCP tools. This server allows clients to interact with Cisco ISE REST APIs in a standardized way, offering features like dynamic tool generation and API response filtering.

## Features

-   **Dynamic Tool Generation:** MCP tools are automatically created based on entries in the `ise_mcp/urls.json` configuration file.
-   **FastMCP Integration:** Leverages the `fastmcp` library for robust MCP server implementation, including schema generation and request handling.
-   **Asynchronous API Calls:** Uses `httpx.AsyncClient` for non-blocking communication with Cisco ISE.
-   **API Filtering:** Supports filtering of Cisco ISE API results through `filter_expression` and `query_params` arguments in each tool.
-   **Environment-Driven Configuration:** Cisco ISE connection details (base URL, username, password) and SSL verification settings (`ISE_VERIFY_SSL`) are configured via a `.env` file.
-   **Detailed Docstrings:** Dynamically generated tools include comprehensive docstrings explaining their purpose, the ISE API endpoint they target, and how to use filtering parameters.
-   **Standardized Interaction:** Adheres to the Model Context Protocol, allowing interaction via any MCP-compatible client.
-   **Streamable HTTP Transport:** Configured to use `streamable-http` transport by default for web-based access.

## Setup

### Requirements

-   Python 3.9 or higher.
-   Required Python packages are listed in `ise_mcp/requirements.txt`. Install them using:
    ```bash
    pip install -r ise_mcp/requirements.txt
    ```
    Or, if using `uv`:
    ```bash
    uv pip install -r ise_mcp/requirements.txt
    ```
    Key dependencies include `fastmcp`, `httpx`, `pydantic`, and `python-dotenv`. (Ensure `requirements.txt` reflects `httpx` instead of `requests`).

### Configuration

1.  **Environment Variables:**
    Create a `.env` file in the `ise_mcp` directory (i.e., `ise_mcp/.env`) with your Cisco ISE API credentials and base URL:
    ```env
    ISE_BASE="https://your-ise-instance.example.com"
    USERNAME="your-ise-api-username"
    PASSWORD="your-ise-api-password"
    # Optional: Controls SSL certificate verification for ISE API calls.
    # Default is true. Set to "false" to disable (insecure).
    # Or provide a path to a CA bundle file, e.g., "/path/to/your/ca.pem".
    ISE_VERIFY_SSL="true"
    ```

2.  **URL Configuration (`urls.json`):**
    Ensure the `ise_mcp/urls.json` file (located in the same directory as `ise_mcp.py`) is present and structured correctly. This file defines the ISE API endpoints that will be exposed as MCP tools.
    ```json
    [
      {
        "URL": "/ers/config/endpoint",
        "Name": "Endpoints",
        "FilterableFields": ["mac", "name", "description", "identityGroupName"]
      },
      {
        "URL": "/ers/config/identitygroup",
        "Name": "Identity Groups",
        "FilterableFields": ["name", "description"]
      }
      // ... more endpoints
    ]
    ```
    -   `URL`: The relative path of the Cisco ISE API endpoint.
    -   `Name`: A human-readable name used to derive the MCP tool name (e.g., "Endpoints" becomes the tool `endpoints`).
    -   `FilterableFields`: An array of strings listing known fields that can be used with the `filter_expression` for this endpoint. This list is user-maintained and crucial for effective filtering.

## Running the Server

The server is implemented in `ise_mcp.py`.

### Standard Execution (Streamable HTTP)

To run the server directly using Python:
```bash
python ise_mcp.py
```
By default, this will start the server using `streamable-http` transport, typically available at `http://127.0.0.1:8000/mcp` (the exact URL and port can be configured in `ise_mcp.py`).

### Development and Testing with MCP Inspector

For development and testing, you can use the `fastmcp dev` command with the MCP Inspector. This provides a UI to interact with your MCP server.
```bash
python -m fastmcp dev ise_mcp.py --with httpx --with pydantic --with python-dotenv
```
After running this command, the MCP Inspector will launch.
-   **For STDIO testing with Inspector:**
    1.  Select "STDIO" as the transport type in the Inspector.
    2.  Set the command to run the server as `python ise_mcp.py`.
    3.  Connect to the server.
-   **For HTTP testing with Inspector:**
    1.  Run `python ise_mcp.py` in a separate terminal to start the server.
    2.  In the MCP Inspector, select "HTTP" or "SSE" (if Streamable HTTP is used, "HTTP" should work for basic interaction, or use a client that fully supports Streamable HTTP).
    3.  Set the URL to `http://127.0.0.1:8000/mcp` (or your configured endpoint).
    4.  Connect to the server.

## Interacting with the Server

Once running, the ISE MCP Server can be accessed using any MCP-compatible client (e.g., MCP Inspector).

### Tool Discovery

Clients can discover available tools. Each tool corresponds to an entry in `urls.json`. Tool names are derived from the `Name` field (e.g., "Identity Groups" becomes `identity_groups`).

### Calling a Tool

Tools are called with a single optional argument, `params`, which is an instance of a Pydantic model (`FilterableToolInput` or `NonFilterableToolInput`).

**Example: Calling the `endpoints` tool without filters:**
An MCP client would typically allow calling the tool without explicit arguments if the tool's input model uses `default_factory`.

**Example: Calling the `endpoints` tool with filters:**
The arguments would be structured according to the Pydantic model. For a tool generated from an endpoint with `FilterableFields`:
```json
// Example arguments for a tool call (client-dependent format)
{
  "params": {
    "filter_expression": "name.CONTAINS.mydevice",
    "query_params": {
      "size": 10,
      "page": 1
    }
  }
}
```
-   `filter_expression` (string, optional): Specifies filters in the format `fieldName.OPERATION.value` (e.g., `mac.EQUALS.AA:BB:CC:DD:EE:FF`). Refer to the tool's docstring for available `FilterableFields` and supported ISE operations (e.g., CONTAINS, EQUALS, STARTSWITH).
-   `query_params` (dict, optional): Allows specifying other arbitrary query parameters (e.g., `{"size": 100, "page": 2}`). These are passed directly to the ISE API.

If an endpoint in `urls.json` has an empty `FilterableFields` array, the corresponding tool will only accept `query_params`.

Refer to the dynamically generated docstring of each tool for specific details on its endpoint and available filterable fields.

## Logging

The server uses the standard Python `logging` module, configured by `fastmcp`. Log messages related to server operations and API interactions will be output to the console.

## License

Apache 2.0 License
