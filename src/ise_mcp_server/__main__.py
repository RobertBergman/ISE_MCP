"""
Command-line interface for the ISE MCP Server.
"""
import argparse
import asyncio
import os

from .server import ISEMCPServer
from .config.settings import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TRANSPORT

def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="ISE MCP Server")
    
    parser.add_argument(
        "--host", 
        type=str, 
        default=os.getenv("FASTMCP_SERVER_HOST", DEFAULT_HOST),
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("FASTMCP_SERVER_PORT", DEFAULT_PORT)),
        help=f"Port to bind to (default: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--transport", 
        type=str, 
        default=os.getenv("FASTMCP_SERVER_TRANSPORT", DEFAULT_TRANSPORT),
        choices=["streamable-http", "sse", "stdio"],
        help=f"Transport to use (default: {DEFAULT_TRANSPORT})"
    )
    
    return parser.parse_args()

async def run_server(args):
    """
    Run the ISE MCP Server with the specified arguments.
    
    Args:
        args: Command-line arguments
    """
    server = ISEMCPServer()
    await server.start(
        host=args.host,
        port=args.port,
        transport=args.transport
    )

def main():
    """
    Main entry point.
    """
    args = parse_args()
    asyncio.run(run_server(args))

if __name__ == "__main__":
    main()