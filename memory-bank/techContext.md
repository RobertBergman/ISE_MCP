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

- **Python Environment:** A Python 3 environment (e.g., 3.13 as seen in logs). Virtual environments (e.g., `.venv`) are in use.
- **IDE:** VS Code.
- **Dependencies:** Managed via `requirements.txt` (contents: `requests`, `pydantic`, `python-dotenv`, `fastmcp`). Installed using `pip` or `uv pip`.
- **`.env` File:** Required at the root of the `ise_mcp` project directory (or in the current working directory when running `main.py`) to store:
    - `ISE_BASE="https://your-ise-ip-or-hostname"`
    - `USERNAME="your-ise-api-username"`
    - `PASSWORD="your-ise-api-password"`
    - `ISE_VERIFY_SSL="true"` (or `false`, or path to CA bundle)
- **`urls.json`:** Must be present in the same directory as `main.py` (now `ise_mcp.py`). Path is resolved using `pathlib`.

## Technical Constraints

- **Cisco ISE API:** Same as previously noted.
- **Filtering Capabilities:** Same as previously noted.
- **Read-Only Operations:** Same as previously noted.
- **`streamable-http` Transport:** The server is configured to use `streamable-http` transport by default in `_main_async`.
- **FastMCP Version:** The version of `fastmcp` must support features like `mcp.run_async(transport="streamable-http")`, `mcp.get_tools()`, and the Pydantic integration for tool argument handling (including `default_factory` behavior). The CLI component (`fastmcp dev`) also has its own dependencies and behaviors (e.g., expecting a `dependencies` attribute on the server object).

## Dependencies

- `fastmcp`
- `httpx` (replaced `requests`)
- `python-dotenv`
- `pydantic` (likely a specific version compatible with the `fastmcp` version in use)

(A `requirements.txt` file exists and lists these. It should be updated to reflect `httpx`.)

## Tool Usage Patterns

- **Running the Server (Standalone with Streamable HTTP):**
    ```bash
    python ise_mcp.py
    ```
    (This will start the server on `http://127.0.0.1:8000` by default, as configured in `_main_async`)
- **Running with MCP Inspector (Recommended for testing):**
    ```bash
    python -m fastmcp dev ise_mcp.py --with httpx --with pydantic --with python-dotenv
    ```
    This command is used due to potential PATH issues with directly calling `fastmcp`. The MCP Inspector will then need to be configured for STDIO transport (as `fastmcp dev` primarily supports this for the Inspector UI), with the command to run the server being `python ise_mcp.py`. Alternatively, to test with HTTP transport, run `python ise_mcp.py` separately and connect the Inspector to `http://127.0.0.1:8000/mcp` (or the configured path).
- **MCP Client:** MCP Inspector is the primary client used for testing.
- **Version Control:** Git with a `.gitignore` file.
- **Debugging:** Python `logging` module, Pylance for static analysis in VS Code, and tracebacks from runtime errors.
