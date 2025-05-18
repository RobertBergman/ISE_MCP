# Technical Context

## Technologies Used

- **Python:** The primary programming language for the server (version 3.13 indicated in some tracebacks).
- **`fastmcp`:** The core library used to implement the Model Context Protocol server. This handles MCP communication, tool registration, schema generation from type hints, and server lifecycle.
- **`httpx`:** Python library used for making asynchronous HTTP GET requests to the Cisco ISE API.
- **`python-dotenv`:** Used to load environment variables from a `.env` file (for ISE credentials, base URL, and SSL settings).
- **`pydantic`:** Used explicitly to define `FilterableToolInput` and `NonFilterableToolInput` models for tool arguments. `fastmcp` also relies heavily on Pydantic for validating arguments against function signatures and generating schemas. `Field(default_factory=...)` is used to make Pydantic model arguments optional.
- **`asyncio`:** Used for managing asynchronous operations, particularly for the server's main execution loop (`_main_async`), `httpx` calls, and for `fastmcp` methods like `get_tools()` and `run_async()`.
- **JSON:** Used for the `urls.json` configuration file and for data exchange with the Cisco ISE API.
- **`sys`:** Used for `sys.exit()` to terminate the script if critical environment variables are missing.
- **`pathlib`:** Used for robust file path manipulation, especially for loading `urls.json`.
- **`logging`:** Standard Python logging library for application logs.
- **`os`:** Used for interacting with environment variables.

## Development Setup

- **Python Environment:** A Python 3 environment (e.g., 3.13 as seen in logs). Virtual environments (e.g., `.venv`) are in use for local development.
- **Docker:** The server can be run as a Docker container using the `isemcp:latest` image.
- **IDE:** VS Code.
- **Dependencies:** Managed via `requirements.txt` (contents: `requests`, `pydantic`, `python-dotenv`, `fastmcp`). Installed using `pip` or `uv pip` for local development. These are also handled within the Docker image.
- **`.env` File:** Required at the root of the `ISE_MCP` project directory. The server script (`src/cisco/ISE/ise_mcp_server/server.py`) expects `urls.json` to be in its own directory (`src/cisco/ISE/ise_mcp_server/`). Within the Docker container, `server.py` and `urls.json` are copied to `/app/`. Stores:
    - `ISE_BASE="https://your-ise-ip-or-hostname"`
    - `USERNAME="your-ise-api-username"`
    - `PASSWORD="your-ise-api-password"`
    - `ISE_VERIFY_SSL="true"` (or `false`, or path to CA bundle)
- **`urls.json`:** Located at `src/cisco/ISE/ise_mcp_server/urls.json`. Path is resolved using `pathlib` relative to the server script. Inside the Docker container, it's copied to `/app/urls.json`.

## Technical Constraints

- **Cisco ISE API:** Same as previously noted.
- **Filtering Capabilities:** Same as previously noted.
- **Read-Only Operations:** Same as previously noted.
- **`streamable-http` Transport:** The server is configured to use `streamable-http` transport by default in `_main_async`. This applies to both local and Docker execution.
- **FastMCP Version:** The version of `fastmcp` must support features like `mcp.run_async(transport="streamable-http")`, `mcp.get_tools()`, and the Pydantic integration for tool argument handling (including `default_factory` behavior). The CLI component (`fastmcp dev`) also has its own dependencies and behaviors (e.g., expecting a `dependencies` attribute on the server object).
- **Docker Image:** The `isemcp:latest` Docker image encapsulates the server and its dependencies. The Dockerfile is configured to use `stdio` transport for compatibility with Claude Desktop and Docker Desktop AI Tools.
- **Claude Desktop Configuration:** The `claude_desktop_config.json` (or `cline_mcp_settings.json`) is configured to run the "ISE_MCP" server using `docker run -i --rm --env-file=.env ise-mcp:latest`.

## Dependencies

- `fastmcp`
- `httpx` (replaced `requests`)
- `python-dotenv`
- `pydantic` (likely a specific version compatible with the `fastmcp` version in use)

(A `requirements.txt` file exists and lists these. It should be updated to reflect `httpx`. These are managed within the Docker image as well.)

## Tool Usage Patterns

- **Running the Server with Docker for Claude Desktop (Primary Method):**
    - **Build Image:**
      ```bash
      docker build -t ise-mcp:latest .
      ```
    - **Claude Desktop Configuration (`claude_desktop_config.json`):**
      ```json
      "ISE_MCP": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "--env-file=/Users/berg276/mcp_servers/ISE_MCP/.env", // Absolute path to .env
          "ise-mcp:latest"
        ],
        "cwd": "/Users/berg276/mcp_servers/ISE_MCP" // Project root
      }
      ```
    This setup ensures Claude Desktop runs the Docker container in interactive mode (`-i`) for STDIO, passes environment variables from the host's `.env` file without including it in the image, and uses the correct working directory.
- **Running with Docker Compose (Local Testing Alternative):**
    ```bash
    docker-compose up --build
    ```
    The `docker-compose.yml` builds the image from the local `Dockerfile` and uses `env_file: - .env` to load environment variables. This is suitable for local testing but not the primary method for Claude Desktop integration.
- **Running Standalone Locally (without Docker):**
    ```bash
    python src/cisco/ISE/ise_mcp_server/server.py
    ```
    (This will start the server using the transport configured in `src/cisco/ISE/ise_mcp_server/server.py` - by default `streamable-http` on `http://127.0.0.1:8000/mcp`. The `server.py` script can be modified to use `stdio` or other transports if needed for direct local execution with specific clients.)
- **Running Standalone Locally with `uv` and `fastmcp run` (STDIO):**
    ```bash
    uv --directory /Users/berg276/mcp_servers/ISE_MCP run fastmcp run src/cisco/ISE/ise_mcp_server/server.py --transport stdio
    ```
    (This method is useful for STDIO clients and ensures `fastmcp` handles `.env` loading within the specified directory. Can be configured in Claude Desktop with a distinct server key like "ISE_LOCAL_UV".)
- **Running with MCP Inspector (STDIO testing of `src/cisco/ISE/ise_mcp_server/server.py` directly):**
    ```bash
    python -m fastmcp dev src/cisco/ISE/ise_mcp_server/server.py --with httpx --with pydantic --with python-dotenv
    ```
    Configure Inspector for STDIO and command `python src/cisco/ISE/ise_mcp_server/server.py`.
- **MCP Client:**
    - **Claude Desktop:** Configured to use the `docker run` command specified above.
    - **MCP Inspector:** Can be used for testing either the STDIO transport (via `fastmcp dev`) or HTTP transport (by running `python src/cisco/ISE/ise_mcp_server/server.py` and connecting to the HTTP endpoint).
- **Version Control:** Git with a `.gitignore` file.
- **Debugging:** Python `logging` module, Pylance for static analysis in VS Code, and tracebacks from runtime errors.
