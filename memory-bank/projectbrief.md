# Project Brief

## Core Requirements and Goals

- To create a Model Context Protocol (MCP) server that provides tools for interacting with a Cisco ISE (Identity Services Engine) instance.
- The server should dynamically generate tools based on a list of Cisco ISE API endpoints.
- Tools should allow for filtering of API results where supported by the Cisco ISE API.
- The server should be implemented using the `fastmcp` Python library.

## Project Scope

**In Scope:**
- Migration of an existing custom JSON-RPC ISE MCP server to use the `fastmcp` library.
- Dynamic generation of MCP tools from a `urls.json` configuration file.
- Implementation of filtering capabilities for the generated tools, allowing users to pass filter expressions and query parameters.
- Generation of informative docstrings for each tool, including guidance on filtering and available filterable fields.
- Use of `httpx.AsyncClient` for asynchronous API calls.
- Configuration of SSL verification for ISE API calls via environment variables.
- Server transport configured to `streamable-http`.

**Out of Scope:**
- Comprehensive research and population of all possible filterable fields for every Cisco ISE API endpoint (this requires external documentation lookup by the user/developer).
- Implementation of Cisco ISE API endpoints beyond GET requests (e.g., POST, PUT, DELETE).
- Advanced error handling or retry logic beyond what `httpx` and `fastmcp` provide by default.
- User authentication/authorization for the MCP server itself (relies on Cisco ISE credentials for API calls).

## Key Stakeholders

- Developers or users who need to interact with Cisco ISE programmatically via an MCP interface.
- Cline (myself), for maintaining and extending this server.

## Success Metrics

- The MCP server successfully connects to and interacts with the Cisco ISE API.
- All tools defined in `urls.json` are correctly registered and discoverable.
- Tools can be called with and without filter parameters, and the API calls reflect these parameters.
- Docstrings for tools provide clear instructions on usage and filtering.
- The server operates reliably using the `fastmcp` library.
