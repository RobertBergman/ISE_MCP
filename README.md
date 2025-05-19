# ISE MCP Server (using FastMCP)

## Overview

The ISE MCP Server is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server built with the Python [`fastmcp`](https://gofastmcp.com/) library. It dynamically exposes Cisco Identity Services Engine (ISE) API endpoints as structured, discoverable MCP tools. This server allows clients to interact with Cisco ISE REST APIs in a standardized way, offering features like dynamic tool generation and API response filtering.

## Features

-   **Dynamic Tool Generation:** MCP tools are automatically created based on entries in the `src/ise_mcp_server/urls.json` configuration file.
-   **FastMCP Integration:** Leverages the `fastmcp` library for robust MCP server implementation, including schema generation and request handling.
-   **Asynchronous API Calls:** Uses `httpx.AsyncClient` for non-blocking communication with Cisco ISE.
-   **API Filtering:** Supports filtering of Cisco ISE API results through `filter_expression` and `query_params` arguments in each tool.
-   **Environment-Driven Configuration:** Cisco ISE connection details (base URL, username, password) and SSL verification settings (`ISE_VERIFY_SSL`) are configured via a `.env` file.
-   **Detailed Docstrings:** Dynamically generated tools include comprehensive docstrings explaining their purpose, the ISE API endpoint they target, and how to use filtering parameters.
-   **Standardized Interaction:** Adheres to the Model Context Protocol, allowing interaction via any MCP-compatible client.
-   **Streamable HTTP Transport:** Configured to use `streamable-http` transport by default for web-based access.

## Setup

## Server 
{
  "mcpServers": {
    "ise": {
      "command": "python",
      "args": [
        "ise_mcp_server.py",
        "--oneshot"
      ],
      "env": {
        "ISE_BASE": "https://devnetsandboxise.cisco.com",
        "USERNAME": "readonly",
        "PASSWORD": "ISEisC00L"
      }
    }
  }
}

### Requirements

-   Python 3.9 or higher.
-   Required Python packages are listed in `requirements.txt` (at the project root). Install them using:
    ```bash
    pip install -r requirements.txt
    ```
    Or, if using `uv`:
    ```bash
    uv pip install -r requirements.txt
    ```
    Key dependencies include `fastmcp`, `httpx`, `pydantic`, and `python-dotenv`. (Ensure `requirements.txt` reflects `httpx` instead of `requests`).

### Configuration

1.  **Environment Variables:**
    Create a `.env` file in the project root directory (`/Users/username/mcp_servers/ISE_MCP/.env`) with your Cisco ISE API credentials and base URL:
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
    Ensure the `src/ise_mcp_server/urls.json` file (located in the same directory as `src/ise_mcp_server/server.py`) is present and structured correctly. This file defines the ISE API endpoints that will be exposed as MCP tools.
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

## Running the Server with Docker for Claude Desktop

This server is designed to be run as a Docker container, especially when used with clients like Claude Desktop that interact via STDIO.

### Prerequisites
1.  **Docker Installed:** Ensure Docker Desktop is installed and running.
2.  **`.env` File:** Your `.env` file (as described in Configuration) must be present in the project root (`/Users/username/mcp_servers/ISE_MCP/.env`).
3.  **Dockerfile Configured for STDIO:** The `Dockerfile` in this project (`Dockerfile`) should be configured to use `stdio` transport. The `ENTRYPOINT` should look like:
    ```dockerfile
    ENTRYPOINT ["python", "-m", "ise_mcp_server", "--transport", "stdio"]
    ```
    Ensure it does *not* copy the `.env` file.

### Build the Docker Image
Navigate to the directory containing the Dockerfile (`/Users/username/mcp_servers/ISE_MCP/`) and build the Docker image:
```bash
docker build -t ise-mcp:latest .
```
Alternatively, if building from the project root:
```bash
docker build -t ise-mcp:latest -f src/Dockerfile .
```

### Configure Claude Desktop
Update your Claude Desktop MCP server configuration (`claude_desktop_config.json` or `cline_mcp_settings.json`) for the "ISE_MCP" server as follows:

```json
{
  "mcpServers": {
    // ... other servers ...
    "ISE_MCP": {
      "command": "docker",
      "args": [
        "run",
        "-i",         // Essential for STDIO interaction
        "--rm",       // Automatically remove the container when it exits
        "--env-file=/Users/username/mcp_servers/ISE_MCP/.env", // Mounts your .env file
        "ise-mcp:latest" // The image we just built
      ],
      "cwd": "/Users/username/mcp_servers/ISE_MCP" // Ensures paths are correct
    }
    // ... other servers ...
  }
}
```
**Explanation of Docker arguments:**
-   `run`: Executes the Docker container.
-   `-i`: (Interactive) Keeps STDIN open even if not attached, crucial for STDIO-based MCP communication.
-   `--rm`: Automatically removes the container when it exits.
-   `--env-file`: Specifies the path to your `.env` file on your host machine. Docker will load these variables into the container.
-   `ise-mcp:latest`: The name and tag of the Docker image to run.
-   `cwd`: Sets the working directory for the command, ensuring that relative paths (like for `--env-file`) are resolved correctly if Claude Desktop runs commands from a different default directory.

### Running with Docker Compose (Alternative for local testing)
A `docker-compose.yml` file is also provided for local testing. It builds the image and runs the container, loading environment variables from the `.env` file.
```bash
docker-compose up --build
```
This method is suitable for direct testing but the `docker run` configuration above is preferred for Claude Desktop integration.

## Running the Server Locally (without Docker)

For development or when Docker is not preferred, you can run the server directly using Python.

### Prerequisites
1.  **Python Environment:** Ensure you have Python 3.9+ and have installed the dependencies from `requirements.txt`.
2.  **`.env` File:** The `.env` file must be present in the project root (`/Users/username/mcp_servers/ISE_MCP/.env`).

### Execution
Navigate to the project root directory and run:
```bash
python src/ise_mcp_server/server.py
```
By default, `src/ise_mcp_server/server.py` is configured to start the server using `streamable-http` transport, typically available at `http://127.0.0.1:8000/mcp`. You can modify `server.py` to change the transport (e.g., to `stdio`) or other server parameters if needed for your specific client.

### Development and Testing with MCP Inspector (Local Python)
For local development with the MCP Inspector:
```bash
python -m fastmcp dev src/ise_mcp_server/server.py --with httpx --with pydantic --with python-dotenv
```
After running this command, the MCP Inspector will launch.
-   **For STDIO testing with Inspector:**
    1.  Select "STDIO" as the transport type in the Inspector.
    2.  Set the command to run the server as `python src/ise_mcp_server/server.py`.
    3.  Connect to the server.
-   **For HTTP testing with Inspector:**
    1.  Run `python src/ise_mcp_server/server.py` in a separate terminal to start the server (it will use `streamable-http` by default).
    2.  In the MCP Inspector, select "HTTP".
    3.  Set the URL to `http://127.0.0.1:8000/mcp` (or your configured endpoint).
    4.  Connect to the server.

### Running Locally with `uv` and `fastmcp run` (Alternative for STDIO)
If you have `uv` and `fastmcp` installed globally or in your environment, you can also run the server using the `fastmcp run` command, which is often useful for STDIO-based clients.

**Prerequisites:**
1.  `uv` installed and in your PATH.
2.  `fastmcp` installed in the environment `uv` will use (or globally).
3.  `.env` file present in the project root.

**Execution:**
```bash
uv --directory /Users/username/mcp_servers/ISE_MCP run fastmcp run src/ise_mcp_server/server.py --transport stdio
```
This command tells `uv` to execute `fastmcp run src/ise_mcp_server/server.py --transport stdio` within the specified project directory. The `--transport stdio` flag is important for clients expecting STDIO.

**Claude Desktop Configuration for `uv` method:**
If you prefer this method for Claude Desktop, you can configure it as follows:
```json
{
  "mcpServers": {
    // ... other servers ...
    "ISE_LOCAL_UV": { // Using a different key to distinguish
      "command": "uv",
      "args": [
        "--directory",
        "/Users/username/mcp_servers/ISE_MCP",
        "run",
        "fastmcp",
        "run",
        "src/ise_mcp_server/server.py",
        "--transport",
        "stdio"
      ],
      "cwd": "/Users/username/mcp_servers/ISE_MCP", // Ensures .env is found if relative paths are used by fastmcp for .env loading
      "transportType": "stdio" // Explicitly tell Claude this is an STDIO server
    }
    // ... other servers ...
  }
}
```
This configuration will be picked up by Claude Desktop if you name your server "ISE_LOCAL_UV" or adjust the key accordingly. Note that `fastmcp run` will automatically load the `.env` file from the current working directory (`/Users/username/mcp_servers/ISE_MCP` in this case).

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
