# Product Context

## Why This Project Exists

This project, `ise_mcp`, was initiated to provide a standardized and more robust way to interact with the Cisco ISE (Identity Services Engine) API. The original implementation used a custom JSON-RPC mechanism. Migrating to `fastmcp` (a Python library for building Model Context Protocol servers) aims to leverage a more standardized protocol, improve maintainability, and potentially benefit from the growing MCP ecosystem.

## Problems It Solves

- **Standardization:** Replaces a custom JSON-RPC implementation with the Model Context Protocol, making it easier for various clients and tools designed for MCP to interact with Cisco ISE.
- **Maintainability:** `fastmcp` provides a higher-level framework, reducing boilerplate code for server implementation and tool definition.
- **Discoverability:** MCP provides standard mechanisms for tool discovery, which `fastmcp` implements.
- **Enhanced Functionality:** The migration provided an opportunity to add features like API response filtering directly into the MCP tools.

## How It Should Work

The `ise_mcp` server operates as follows:
1.  On startup, it reads a `urls.json` file. This file contains a list of Cisco ISE API endpoints, each with a name and a relative URL.
2.  For each entry in `urls.json`, the server dynamically creates and registers an MCP tool.
3.  The name of the tool is derived from the "Name" field in `urls.json` (e.g., "Endpoints" becomes `endpoints`).
4.  Each tool, when called, makes a GET request to the corresponding Cisco ISE API endpoint (e.g., `GET {ISE_BASE}/ers/config/endpoint`).
5.  Credentials for Cisco ISE (base URL, username, password) are read from environment variables.
6.  Tools accept optional parameters for filtering:
    *   `filter_expression` (string): Allows specifying filters in the format `fieldName.OPERATION.value` (e.g., `name.CONTAINS.mydevice`). This is passed as the `filter` query parameter to the ISE API.
    *   `query_params` (dictionary): Allows specifying other arbitrary query parameters (e.g., `{'size': 10, 'page': 1}`). These are merged with the API request.
7.  The server generates detailed docstrings for each tool, explaining its purpose, the API endpoint it calls, how to use the filtering parameters, and listing known filterable fields (if defined in `src/cisco/ISE/ise_mcp_server/urls.json`).
8.  The server communicates with MCP clients via `streamable-http` transport by default (e.g., `http://127.0.0.1:8000/mcp`), as configured in `src/cisco/ISE/ise_mcp_server/server.py`.
9.  SSL verification for connections to Cisco ISE can be configured via the `ISE_VERIFY_SSL` environment variable (true, false, or path to CA bundle).
10. The server uses `httpx.AsyncClient` for making asynchronous API calls to Cisco ISE.

Users interact with this server through an MCP-compatible client. They can discover available tools (each corresponding to an ISE API endpoint) and call them, optionally providing filter criteria to refine the data retrieved from Cisco ISE.

## User Experience Goals

- **Ease of Use:** Users should find it straightforward to discover and call tools corresponding to Cisco ISE API endpoints.
- **Clarity:** Tool names and descriptions (docstrings) should clearly indicate what data each tool fetches and how to use filtering.
- **Power:** The filtering mechanism should provide users with sufficient control to retrieve specific subsets of data from ISE.
- **Reliability:** The server should reliably proxy requests to Cisco ISE and return responses or appropriate error messages.
- **Standard Compliance:** Adherence to MCP allows users to leverage familiar MCP clients and workflows.
