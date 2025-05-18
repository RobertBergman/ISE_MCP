# Cisco ISE MCP Server

This project provides a Model Context Protocol (MCP) server for interacting with a Cisco Identity Services Engine (ISE) instance. It is built using the `fastmcp` Python library and dynamically generates MCP tools based on a configurable list of Cisco ISE API endpoints.

## Key Features

- **Dynamic Tool Generation**: MCP tools are automatically created based on API endpoint definitions in `src/cisco/ISE/ise_mcp_server/urls.json`.
- **API Filtering**: Supports filtering of API results for endpoints that allow it. Filter expressions and query parameters can be passed to the tools.
- **Asynchronous Operations**: Utilizes `httpx.AsyncClient` for non-blocking API calls to Cisco ISE.
- **`fastmcp` Based**: Leverages the `fastmcp` library for robust and efficient MCP server implementation.
- **Configurable SSL Verification**: SSL certificate verification for ISE API calls can be configured via environment variables.

## Project Structure

- `src/cisco/ISE/ise_mcp_server/`: Contains the core server logic.
  - `server.py`: The main FastMCP server application.
  - `urls.json`: Defines the Cisco ISE API endpoints to be exposed as MCP tools.
- `src/cisco/ISE/Dockerfile`: Dockerfile for containerizing the MCP server.
- `memory-bank/`: Contains project documentation and context for Cline (AI Software Engineer).

## Getting Started

### Prerequisites

- Python 3.8+
- Access to a Cisco ISE instance
- Docker (optional, for containerized deployment)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r src/cisco/ISE/requirements.txt
    ```

### Configuration

The server requires environment variables to connect to your Cisco ISE instance and for other configurations. Create a `.env` file in the `src/cisco/ISE/` directory with the following content:

```env
ISE_BASE_URL=https://your-ise-instance.com
ISE_USERNAME=your_ise_username
ISE_PASSWORD=your_ise_password
ISE_VERIFY_SSL=true  # Set to false to disable SSL verification (not recommended for production)
# For FastMCP server running in HTTP mode
FASTMCP_SERVER_TRANSPORT=streamable-http # or sse
FASTMCP_SERVER_HOST=0.0.0.0
FASTMCP_SERVER_PORT=8000
```

Replace the placeholder values with your actual Cisco ISE details.

### Running the Server

You can run the server directly using Python:

```bash
python src/cisco/ISE/ise_mcp_server/server.py
```

Alternatively, you can use the `fastmcp` CLI:

```bash
fastmcp run src/cisco/ISE/ise_mcp_server/server.py
```

The server will start, and by default (if `FASTMCP_SERVER_TRANSPORT` is `streamable-http`), it will be accessible at `http://<FASTMCP_SERVER_HOST>:<FASTMCP_SERVER_PORT>/mcp`.

### Docker Deployment

A Dockerfile is provided for containerized deployment:

1.  **Build the Docker image:**
    ```bash
    docker build -t ise-mcp-server -f src/cisco/ISE/Dockerfile src/cisco/ISE/
    ```

2.  **Run the Docker container:**
    Make sure to pass the environment variables, for example by using an env-file.
    ```bash
    docker run -p 8000:8000 --env-file src/cisco/ISE/.env ise-mcp-server
    ```
    This will map port 8000 of the container to port 8000 on your host.

## Defining Tools (`urls.json`)

The MCP tools are dynamically generated from the `src/cisco/ISE/ise_mcp_server/urls.json` file. Each entry in this JSON file defines an API endpoint that will be turned into an MCP tool.

Example entry in `urls.json`:
```json
{
  "endpoints": {
    "tool_name": "endpoints",
    "path": "/ers/config/endpoint?size=100",
    "description": "Fetch data for Endpoints from Cisco ISE",
    "filterable_fields": ["name", "description", "mac", "groupId", "staticGroupAssignment", "identityStore", "portalUser", "mdmServerName", "deviceType", "operatingSystem"]
  }
  // ... other endpoints
}
```

- `tool_name`: The name of the MCP tool that will be generated.
- `path`: The API endpoint path on the Cisco ISE server.
- `description`: A description for the generated MCP tool.
- `filterable_fields`: An array of strings listing the fields that can be used for filtering via the tool's `filter_expression` parameter.

## Using the Tools

Once the server is running, MCP clients can connect to it and use the generated tools. Each tool will have a docstring providing its description and information on available filterable fields.

Example of calling a tool (conceptual):
```python
# Assuming 'client' is an MCP client connected to the server
# Fetch all endpoints
all_endpoints = await client.call_tool("endpoints")

# Fetch endpoints filtering by name
filtered_endpoints = await client.call_tool(
    "endpoints",
    {"params": {"filter_expression": "name.CONTAINS.some-device-name"}}
)
```

## Contributing

Contributions are welcome! Please refer to the project's contribution guidelines (if available) or open an issue to discuss potential changes.

## License

This project is licensed under the [MIT License](LICENSE).
