# ISE MCP Server - Modular Structure

This is a restructured version of the ISE MCP Server with a more modular design. The key improvements in this version include:

## Directory Structure

```
ise_mcp_server/
├── __init__.py
├── __main__.py          # Command-line entry point
├── server.py            # Main server class
├── config/              # Configuration-related modules
│   ├── __init__.py
│   ├── settings.py      # Environment variables and settings
│   ├── urls.json        # URL definitions for the API endpoints
│   └── urls_config.py   # Functions to load URLs configuration
├── core/                # Core functionality
│   ├── __init__.py
│   ├── models.py        # Pydantic models for tool inputs
│   └── utils.py         # Utility functions
├── api/                 # API client
│   ├── __init__.py
│   └── client.py        # ISE API client
└── tools/               # Tool-related modules
    ├── __init__.py
    └── factory.py       # Tool factory
```

## Key Components

- **ISEMCPServer**: Main server class in `server.py` that initializes the FastMCP instance, registers tools, and starts the server.
- **ToolFactory**: Factory class in `tools/factory.py` that creates tool functions from URL definitions.
- **ISEApiClient**: Client class in `api/client.py` for making API requests to Cisco ISE.
- **Settings**: Configuration module in `config/settings.py` that loads and validates environment variables.
- **URLs Configuration**: Functions in `config/urls_config.py` for loading the URL definitions from a JSON file.
- **Models**: Pydantic models in `core/models.py` for tool inputs.
- **Utilities**: Utility functions in `core/utils.py` for common tasks.

## How to Run

The server can be run directly using the `__main__.py` module:

```bash
python -m ise_mcp_server
```

You can also specify custom host, port, and transport:

```bash
python -m ise_mcp_server --host 0.0.0.0 --port 8080 --transport streamable-http
```

## Docker

The server can also be run as a Docker container using the provided Dockerfile. The Dockerfile has been updated to work with the new modular structure.

## Development

For development, you can install the package in development mode:

```bash
pip install -e .
```

This will make the package available in your Python environment, allowing you to import it from other scripts or run it with the `ise-mcp-server` command.