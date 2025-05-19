# Product Context

## Why This Project Exists

This project, `ise_mcp`, was initiated to provide a standardized and more robust way to interact with the Cisco ISE (Identity Services Engine) API. The original implementation used a custom JSON-RPC mechanism. Migrating to `fastmcp` (a Python library for building Model Context Protocol servers) aims to leverage a more standardized protocol, improve maintainability, and potentially benefit from the growing MCP ecosystem.

## Problems It Solves

- **Standardization:** Replaces a custom JSON-RPC implementation with the Model Context Protocol, making it easier for various clients and tools designed for MCP to interact with Cisco ISE.
- **Maintainability:** `fastmcp` provides a higher-level framework, reducing boilerplate code for server implementation and tool definition.
- **Discoverability:** MCP provides standard mechanisms for tool discovery, which `fastmcp` implements.
- **Enhanced Functionality:** The migration provided an opportunity to add features like API response filtering directly into the MCP tools.
- **Code Organization:** The modular architecture enhances maintainability and makes it easier for developers to understand and extend the codebase.
- **Component Reusability:** The separation of concerns allows for reuse of components like the API client in other contexts.

## How It Should Work

The `ise_mcp` server operates as follows:
1.  On startup, the main server class `ISEMCPServer` initializes.
2.  The server loads configuration settings from environment variables via the `config.settings` module.
3.  The `config.urls_config` module loads the URL definitions from `urls.json`. This file contains a list of Cisco ISE API endpoints, each with a name and a relative URL.
4.  The `ToolFactory` class creates tool functions for each endpoint defined in `urls.json`.
5.  The server registers these tools with FastMCP.
6.  When a tool is called:
    a. The input parameters are parsed using Pydantic models (`FilterableToolInput` or `NonFilterableToolInput`).
    b. The `ISEApiClient` makes an asynchronous GET request to the corresponding Cisco ISE API endpoint.
    c. The API response is returned to the client.
7.  Tools accept optional parameters for filtering:
    *   `filter_expression` (string): Allows specifying filters in the format `fieldName.OPERATION.value` (e.g., `name.CONTAINS.mydevice`). This is passed as the `filter` query parameter to the ISE API.
    *   `query_params` (dictionary): Allows specifying other arbitrary query parameters (e.g., `{'size': 10, 'page': 1}`). These are merged with the API request.
8.  The server generates detailed docstrings for each tool, explaining its purpose, the API endpoint it calls, how to use the filtering parameters, and listing known filterable fields (if defined in `urls.json`).
9.  The server can communicate with MCP clients via different transports:
    * `streamable-http` transport by default for local execution (e.g., `http://127.0.0.1:8000/mcp`).
    * `stdio` transport when run in Docker for Claude Desktop.
10. SSL verification for connections to Cisco ISE can be configured via the `ISE_VERIFY_SSL` environment variable (true, false, or path to CA bundle).
11. The server uses `httpx.AsyncClient` for making asynchronous API calls to Cisco ISE.

Users interact with this server through an MCP-compatible client. They can discover available tools (each corresponding to an ISE API endpoint) and call them, optionally providing filter criteria to refine the data retrieved from Cisco ISE.

## User Experience Goals

- **Ease of Use:** Users should find it straightforward to discover and call tools corresponding to Cisco ISE API endpoints.
- **Clarity:** Tool names and descriptions (docstrings) should clearly indicate what data each tool fetches and how to use filtering.
- **Power:** The filtering mechanism should provide users with sufficient control to retrieve specific subsets of data from ISE.
- **Reliability:** The server should reliably proxy requests to Cisco ISE and return responses or appropriate error messages.
- **Standard Compliance:** Adherence to MCP allows users to leverage familiar MCP clients and workflows.
- **Flexibility:** Command-line options allow for customization of host, port, and transport.
- **Developer Friendliness:** The modular architecture and clear code organization make it easier for developers to understand, maintain, and extend the server.
- **Future Extensibility:** The architecture is designed to accommodate future enhancements like caching, rate limiting, and support for additional HTTP methods.