"""
Main entry point for the ISE MCP Server.
"""
import asyncio
import sys

from fastmcp import FastMCP

from .config.settings import logger, validate_settings, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TRANSPORT
from .config.urls_config import load_urls
from .tools.factory import ToolFactory

class ISEMCPServer:
    """
    ISE MCP Server that provides tools to interact with Cisco ISE APIs.
    """
    
    def __init__(self):
        """
        Initialize the ISE MCP Server.
        """
        # Validate settings before proceeding
        if not validate_settings():
            sys.exit(1)
        
        # Initialize FastMCP
        self.mcp = FastMCP(
            name="ISE MCP Server",
            instructions="Provides tools to fetch data from Cisco ISE. Tools support filtering, pagination, and caching for improved performance."
        )
        self.mcp.dependencies = []  # Required for fastmcp dev compatibility
        
        # Load URLs
        self.urls = load_urls()
        
        # Create tool factory
        self.tool_factory = ToolFactory()
        
    def register_tools(self):
        """
        Register all tools with the MCP server.
        """
        # Register API tools from urls.json
        api_tools_info = self.tool_factory.create_tools_from_url_entries(self.urls)
        for tool_info in api_tools_info:
            self.mcp.add_tool(tool_info["function"])
            logger.info(
                f"✅ Registered API tool: {tool_info['name']} with input model: "
                f"{'FilterableToolInput' if tool_info['supports_filtering'] else 'NonFilterableToolInput'}"
            )
        
        # Register cache management tools
        cache_tools_info = self.tool_factory.create_cache_management_tools()
        for tool_info in cache_tools_info:
            self.mcp.add_tool(tool_info["function"])
            logger.info(f"✅ Registered cache management tool: {tool_info['name']}")
        
        # Register rate limiting management tools
        rate_limit_tools_info = self.tool_factory.create_rate_limit_tools()
        for tool_info in rate_limit_tools_info:
            self.mcp.add_tool(tool_info["function"])
            logger.info(f"✅ Registered rate limit management tool: {tool_info['name']}")
        
        total_tools = len(api_tools_info) + len(cache_tools_info) + len(rate_limit_tools_info)
        
        return total_tools
        
    async def start(self, host=DEFAULT_HOST, port=DEFAULT_PORT, transport=DEFAULT_TRANSPORT):
        """
        Start the MCP server.
        
        Args:
            host: The host to bind to (only used for HTTP transport)
            port: The port to bind to (only used for HTTP transport)
            transport: The transport to use
        """
        num_tools = self.register_tools()
        
        if num_tools == 0:
            logger.error("No tools were registered. Check urls.json and logs. Exiting.")
            return
        
        try:
            # Log server startup
            logger.info(f"🚀 Starting ISE FastMCP Server with {num_tools} tools...")
            
            # Start the server based on transport type
            if transport == "stdio":
                # For stdio transport, we don't need host and port
                await self.mcp.run_async(transport=transport)
            else:
                # For HTTP-based transports, use host and port
                await self.mcp.run_async(transport=transport, host=host, port=port)
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            sys.exit(1)

async def _main_async():
    """
    Asynchronous main function.
    """
    server = ISEMCPServer()
    await server.start()

def main():
    """
    Main entry point.
    """
    asyncio.run(_main_async())

if __name__ == "__main__":
    main()