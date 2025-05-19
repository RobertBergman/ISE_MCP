"""
Test module for the ISE MCP Server.
"""
import unittest
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ise_mcp_server.config.urls_config import load_urls
from ise_mcp_server.tools.factory import ToolFactory

class TestISEMCPServer(unittest.TestCase):
    """
    Test case for the ISE MCP Server.
    """
    
    def test_load_urls(self):
        """
        Test that URLs can be loaded from the configuration file.
        """
        urls = load_urls()
        self.assertIsInstance(urls, list)
        # This test will only pass if the urls.json file is found and loaded successfully
    
    def test_tool_factory(self):
        """
        Test that the ToolFactory can create tools from URL entries.
        """
        # Create a mock URL entry
        entry = {
            "URL": "/test/endpoint",
            "Name": "Test Endpoint",
            "FilterableFields": ["name", "description"]
        }
        
        # Create a tool from the entry
        factory = ToolFactory()
        tool_info = factory.create_tool_from_url_entry(entry)
        
        # Check that the tool was created successfully
        self.assertIsNotNone(tool_info)
        self.assertEqual(tool_info["name"], "test_endpoint")
        self.assertTrue(tool_info["supports_filtering"])
        self.assertEqual(tool_info["filterable_fields"], ["name", "description"])
        
if __name__ == "__main__":
    unittest.main()