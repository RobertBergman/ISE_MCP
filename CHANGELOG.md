# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial migration to `fastmcp` library for MCP server implementation.
- Dynamic tool generation from `urls.json` for Cisco ISE API endpoints.
- Filtering capabilities (`filter_expression`, `query_params`) for dynamically generated tools.
- Pydantic models (`FilterableToolInput`, `NonFilterableToolInput`) for tool arguments, with `default_factory` to handle calls without explicit parameters.
- Dynamic docstring generation for tools, including filtering information.
- Asynchronous main execution loop (`_main_async`) using `asyncio` and `mcp.run_async()`.
- Explicit `mcp.dependencies = []` for compatibility with `fastmcp dev`.
- Memory bank files (`projectbrief.md`, `productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`, `progress.md`) to document project state and evolution.

### Changed
- Replaced custom JSON-RPC server with `fastmcp`.
- Refactored tool function signatures to use an optional Pydantic model instance for parameters.

### Fixed
- Resolved `TypeError` for `FastMCP.add_tool()` related to `input_schema`.
- Corrected `AttributeError` for `mcp.get_tools_mcp()` to `await mcp.get_tools()`.
- Addressed event loop conflicts by using `await mcp.run_async()` in async context.
- Handled `TypeError` in `fastmcp dev` by setting `mcp.dependencies`.
- Resolved `zsh: command not found: fastmcp` by advising `python -m fastmcp dev`.
- Fixed `ValidationError` for missing `params` argument in tools when called from MCP Inspector by using `default_factory` for Pydantic model arguments.
- Corrected indentation errors in `ise_mcp/main.py`.

### Removed
- Custom JSON-RPC server implementation.
