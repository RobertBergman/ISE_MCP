# Technical Context

## Technologies Used

- **Python:** The primary programming language for the server (version 3.13 indicated in some tracebacks).
- **`fastmcp`:** The core library used to implement the Model Context Protocol server. This handles MCP communication, tool registration, schema generation from type hints, and server lifecycle.
- **`httpx`:** Python library used for making asynchronous HTTP GET requests to the Cisco ISE API.
- **`python-dotenv`:** Used to load environment variables from a `.env` file (for ISE credentials, base URL, and SSL settings).
- **`pydantic`:** Used explicitly to define `FilterableToolInput` and `NonFilterableToolInput` models for tool arguments. `fastmcp` also relies heavily on Pydantic for validating arguments against function signatures and generating schemas. `Field(default_factory=...)` is used to make Pydantic model arguments optional.
- **`asyncio`:** Used for managing asynchronous operations, particularly for the server's main execution loop, `httpx` calls, and for `fastmcp` methods like `get_tools()` and `run_async()`.
- **JSON:** Used for the `urls.json` configuration file and for data exchange with the Cisco ISE API.
- **`sys`:** Used for `sys.exit()` to terminate the script if critical environment variables are missing.
- **`pathlib`:** Used for robust file path manipulation, especially for loading `urls.json`.
- **`logging`:** Standard Python logging library for application logs.
- **`os`:** Used for interacting with environment variables.
- **`argparse`:** Added for command-line argument parsing in the new `__main__.py` module.
- **`setuptools`:** Used in the new `setup.py` file to make the package installable.

## Module Organization

The application is now organized into a modular structure:

- **`src/`**: Source directory
  - **`ise_mcp_server/`**: Root package
    - **`__init__.py`**: Package initialization
    - **`__main__.py`**: Command-line entry point with argument parsing
    - **`server.py`**: Main server class definition

  - **`ise_mcp_server/config/`**: Configuration-related modules
    - **`__init__.py`**: Package initialization
    - **`settings.py`**: Environment variables and application settings
    - **`urls.json`**: URL definitions for API endpoints
    - **`urls_config.py`**: Functions to load URL definitions

  - **`ise_mcp_server/core/`**: Core functionality modules
    - **`__init__.py`**: Package initialization
    - **`models.py`**: Pydantic model definitions
    - **`utils.py`**: Utility functions for common tasks

  - **`ise_mcp_server/api/`**: API communication modules
    - **`__init__.py`**: Package initialization
    - **`client.py`**: ISE API client implementation

  - **`ise_mcp_server/tools/`**: Tool-related modules
    - **`__init__.py`**: Package initialization
    - **`factory.py`**: Tool factory for creating MCP tools

- **`src/tests/`**: Directory for unit tests
  - **`__init__.py`**: Package initialization
  - **`test_server.py`**: Tests for the server functionality

## Development Setup

- **Python Environment:** A Python 3 environment (e.g., 3.13 as seen in logs). Virtual environments (e.g., `.venv`) are in use for local development.
- **Docker:** The server can be run as a Docker container using the `ise-mcp:latest` image.
- **IDE:** VS Code.
- **Dependencies:** Managed via `requirements.txt` and now also via `setup.py`. Installed using `pip install -e .` for development. These are also handled within the Docker image.
- **`.env` File:** Required at the root of the `ISE_MCP` project directory. The server now looks for `urls.json` in multiple locations: `ise_mcp_server/config/urls.json` (new location) and `ise_mcp_server/urls.json` (old location). Within the Docker container, the entire package is now installed. Stores:
    - `ISE_BASE="https://your-ise-ip-or-hostname"`
    - `USERNAME="your-ise-api-username"`
    - `PASSWORD="your-ise-api-password"`
    - `ISE_VERIFY_SSL="true"` (or `false`, or path to CA bundle)
- **`urls.json`:** Primary location is now `src/ise_mcp_server/config/urls.json`. Path resolution is handled by the `urls_config.py` module.
- **`setup.py`:** Top-level file that makes the package installable and defines a console script entry point. Uses the src-layout pattern with `find_packages(where="src")` and `package_dir={"": "src"}`.

## Technical Constraints

- **Cisco ISE API:** Same as previously noted.
- **Filtering Capabilities:** Same as previously noted.
- **Read-Only Operations:** Same as previously noted.
- **Transport Options:** The server now supports configurable transport via command-line arguments. Default is still `streamable-http` for local execution and `stdio` for Docker.
- **FastMCP Version:** The version of `fastmcp` must support the same features as before.
- **Docker Image:** The Docker image now installs the entire package instead of just copying individual files. The `ENTRYPOINT` is updated to use the module directly: `python -m ise_mcp_server --transport stdio`.
- **Claude Desktop Configuration:** The configuration remains the same, but the Docker image internals have changed.
- **Python Package Structure:** The application now follows standard Python package conventions with src-layout, which introduces constraints on imports (using relative imports) and file organization.

## Dependencies

- `fastmcp`
- `httpx`
- `python-dotenv`
- `pydantic`
- `setuptools` (for development and building)

These are now defined in both `requirements.txt` and `setup.py`. The Docker image installs dependencies via `pip install -e .` to install the package in development mode.

## Tool Usage Patterns

- **Running the Server with Docker for Claude Desktop (Primary Method):**
    - **Build Image:**
      ```bash
      docker build -t ise-mcp:latest .
      ```
    - **Claude Desktop Configuration:** Remains the same as before.

- **Running with Docker Compose (Local Testing Alternative):**
    ```bash
    docker-compose up --build
    ```
    The `docker-compose.yml` would need to be updated to reflect the new package structure.

- **Running Standalone Locally (as Python Module):**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    python -m src.ise_mcp_server
    ```
    This will start the server using the default settings from `settings.py`. Command-line arguments can be used to customize behavior:
    ```bash
    python -m src.ise_mcp_server --host 0.0.0.0 --port 8080 --transport stdio
    ```

- **Running as Installed Package:**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    pip install -e .
    ise-mcp-server --host 0.0.0.0 --port 8080 --transport streamable-http
    ```
    This installs the package in development mode and makes the `ise-mcp-server` command available.

- **Running Standalone Locally with Python (STDIO):**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    python -m src.ise_mcp_server --transport stdio
    ```

- **Running with MCP Inspector:**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    python -m fastmcp dev src.ise_mcp_server --with httpx --with pydantic --with python-dotenv
    ```
    Configure Inspector for STDIO.

- **Testing:**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    python -m unittest discover -s src/tests
    ```
    This runs the unit tests in the `src/tests` directory.

- **Import Verification:**
    ```bash
    cd /Users/berg276/mcp_servers/ISE_MCP
    python -c "import src.ise_mcp_server; print('Import successful')"
    ```
    This verifies that the package can be imported correctly.

- **MCP Client:**
    - **Claude Desktop:** Configured to use the `docker run` command with the updated image.
    - **MCP Inspector:** Can be used for testing with the updated module structure.

- **Version Control:** Git with a `.gitignore` file.
- **Debugging:** Python `logging` module, Pylance for static analysis in VS Code, and tracebacks from runtime errors.