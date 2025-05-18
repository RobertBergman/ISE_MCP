# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated project directory structure:
  - Main server script moved from `ise_mcp.py` to `src/cisco/ISE/ise_mcp_server/server.py`.
  - `urls.json` moved to `src/cisco/ISE/ise_mcp_server/urls.json`.
- Updated `Dockerfile` `COPY` and `ENTRYPOINT` instructions to reflect new paths.
- Updated all memory bank files (`projectbrief.md`, `productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`, `progress.md`) and `src/cisco/ISE/README.md` with corrected file paths and commands.

### Added
- Initial migration to `fastmcp` library for MCP server implementation.
- Dynamic tool generation from `urls.json` for Cisco ISE API endpoints.
- Filtering capabilities (`filter_expression`, `query_params`) for dynamically generated tools.
- Pydantic models (`FilterableToolInput`, `NonFilterableToolInput`) for tool arguments, with `default_factory` to handle calls without explicit parameters.
- Dynamic docstring generation for tools, including filtering information.
- Asynchronous main execution loop (`_main_async`) using `asyncio` and `mcp.run_async(transport="streamable-http")`.
- Explicit `mcp.dependencies = []` for compatibility with `fastmcp dev`.
- Memory bank files (`projectbrief.md`, `productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`, `progress.md`) to document project state and evolution.
- Robust SSL verification handling for ISE API calls, configurable via `ISE_VERIFY_SSL` environment variable.
- Use of `sys.exit(1)` for graceful termination if critical environment variables are missing.
- Use of `pathlib` for robust `urls.json` path resolution.

### Changed
- Replaced custom JSON-RPC server with `fastmcp`.
- Replaced `requests` library with `httpx` for asynchronous HTTP calls to Cisco ISE.
- Refactored tool function signatures to use an optional Pydantic model instance for parameters.
- Default server transport changed from `stdio` to `streamable-http`.

### Fixed
- Resolved `TypeError` for `FastMCP.add_tool()` related to `input_schema`.
- Corrected `AttributeError` for `mcp.get_tools_mcp()` to `await mcp.get_tools()`.
- Addressed event loop conflicts by using `await mcp.run_async()` in async context.
- Handled `TypeError` in `fastmcp dev` by setting `mcp.dependencies`.
- Resolved `zsh: command not found: fastmcp` by advising `python -m fastmcp dev`.
- Fixed `ValidationError` for missing `params` argument in tools when called from MCP Inspector by using `default_factory` for Pydantic model arguments.
- Corrected indentation errors in `ise_mcp.py`.
- Improved error handling for API calls by specifically catching `httpx.HTTPStatusError` and `httpx.RequestError`.

### Removed
- Custom JSON-RPC server implementation.
- `requests` library dependency (replaced by `httpx`).

## [0.2.0] - 2025-05-18

### Added
- Docker-based setup for running the ISE MCP server, primarily for Claude Desktop integration.
  - `Dockerfile` modified to use `stdio` transport and remove `.env` copying.
  - `claude_desktop_config.json` updated to use `docker run -i --rm --env-file=.env ise-mcp:latest` for STDIO communication.
  - `ISE_MCP.md` tool definition created for Docker Desktop AI Tools.
- Documentation (`README.md`, memory bank files) updated to reflect the new Docker-based workflow.

### Changed
- Default recommended method for running with Claude Desktop is now via Docker, not direct Python execution or `docker-compose`.
- `docker-compose.yml` is now positioned as an alternative for local testing, not the primary integration method for Claude Desktop.
