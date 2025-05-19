#!/bin/bash
# Simple script to test the ISE MCP Server installation

# Install dependencies
pip install pydantic python-dotenv fastmcp httpx

# Install the package in development mode
pip install -e .

# Run the tests
python -m unittest discover -s tests

echo "Tests completed. To run the server:"
echo "python -m ise_mcp_server"