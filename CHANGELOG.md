# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Modular Architecture Implementation:**
  - Reorganized codebase into a proper Python package structure with clear separation of concerns
  - Created explicit ISEMCPServer, ToolFactory, and ISEApiClient classes 
  - Implemented command-line interface with argument parsing in `__main__.py`
  - Added basic unit tests and verification scripts
  - Created `setup.py` with console script entry point

- **Enhanced Filtering and Rate Limiting:**
  - Implemented comprehensive rate limiting with `aiolimiter` using token bucket algorithm
  - Added global and category-based (auth, device, policy) rate limits
  - Created rate limiting management tools: `rate_limit_info` and `rate_limit_config`
  - Integrated exponential backoff for rate limit retries and HTTP 429 handling
  - Enhanced filtering capabilities with comprehensive input models
  
- **Performance Optimizations:**
  - Implemented API response caching with `aiocache` and configurable TTL
  - Added cache management tools: `cache_clear`, `cache_info`, and `cache_config`
  - Implemented transparent auto-pagination for large result sets
  - Added streaming pagination option for memory-efficient processing

### Changed
- **Project Structure Simplification:**
  - Removed the `cisco/ISE` directory layer, moving `ise_mcp_server` directly under `src/`
  - Implemented src-layout pattern for Python packaging
  - Reorganized imports to use relative imports within the package
  - Updated all configuration files and paths for the new structure

- **Docker Improvements:**
  - Updated Dockerfile to use Python module directly instead of fastmcp CLI
  - Fixed Docker build process to properly handle the src-layout structure
  - Added explicit src directory creation in Dockerfile
  - Updated Docker ENTRYPOINT to use `python -m src.ise_mcp_server`
  
- **Transport and Configuration:**
  - Default transport changed from `stdio` to `streamable-http` for local execution
  - Enhanced configuration with improved URL resolution
  - Made transport parameter handling conditional based on transport type
  - Added more detailed logging throughout the application

### Fixed
- **Docker and Execution:**
  - Fixed Docker startup error with stdio transport by conditionally passing parameters
  - Fixed setup.py to correctly use src-layout pattern for Python packaging
  - Fixed directory not found errors in Docker build
  - Fixed module resolution in Docker environment

- **API Interaction:**
  - Improved error handling for API calls by specifically catching HTTP status and request errors
  - Fixed caching issues with paginated requests
  - Enhanced SSL verification configuration handling

- **Tool Registration and Execution:**
  - Fixed issues with argument validation in tool functions
  - Enhanced docstring generation for better tool discoverability
  - Fixed error handling and reporting for API communication issues

### Removed
- **Deprecated Components:**
  - Removed old directory structure with cisco/ISE layer
  - Removed dependency on fastmcp CLI for running the server
  - Eliminated duplicate configuration files

## [0.3.0] - 2025-05-19

### Added
- **Rate Limiting Implementation:**
  - Added rate limiting models and configuration for Cisco ISE API
  - Implemented token bucket algorithm with aiolimiter library
  - Created rate limiting tools for management and monitoring
  - Added category-based rate limiting for different API endpoints
  - Integrated exponential backoff for rate limit handling

- **Caching and Pagination:**
  - Implemented API response caching with aiocache
  - Added automatic pagination for large result sets
  - Created cache management tools
  - Implemented efficient pagination with caching support

### Changed
- **Project Structure:**
  - Simplified directory structure by removing cisco/ISE layer
  - Implemented src-layout pattern for Python packaging
  - Updated Docker configuration to handle new structure
  - Reorganized imports and module organization

### Fixed
- Fixed Docker startup issues with stdio transport
- Fixed setup.py configuration for src-layout
- Improved error handling for API communication
- Enhanced SSL verification configuration

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

## [0.1.0] - 2025-05-17

### Added
- Initial migration to `fastmcp` library for MCP server implementation.
- Dynamic tool generation from `urls.json` for Cisco ISE API endpoints.
- Filtering capabilities (`filter_expression`, `query_params`) for dynamically generated tools.
- Pydantic models (`FilterableToolInput`, `NonFilterableToolInput`) for tool arguments.
- Dynamic docstring generation for tools, including filtering information.
- Asynchronous API calls with `httpx` and asynchronous server operation.
- Robust SSL verification handling for ISE API calls, configurable via environment variables.
- Memory bank files for documentation and project tracking.

### Changed
- Replaced custom JSON-RPC server with `fastmcp`.
- Replaced `requests` library with `httpx` for asynchronous HTTP calls.

### Fixed
- Various compatibility issues with the `fastmcp` library.
- Error handling improvements for API communication.
