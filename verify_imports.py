"""
Script to verify that all imports in the restructured application work correctly.
"""
import importlib
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

modules_to_check = [
    "ise_mcp_server.config.settings",
    "ise_mcp_server.config.urls_config",
    "ise_mcp_server.core.models",
    "ise_mcp_server.core.utils",
    "ise_mcp_server.api.client",
    "ise_mcp_server.tools.factory",
    "ise_mcp_server.server",
    "ise_mcp_server.__main__",
]

def verify_imports():
    """
    Try to import each module and report any issues.
    """
    success_count = 0
    failure_count = 0
    
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to import {module_name}: {e}")
            failure_count += 1
    
    print(f"\nImport verification complete: {success_count} successes, {failure_count} failures")
    
    return failure_count == 0

if __name__ == "__main__":
    print("Verifying imports for the ISE MCP Server modules...\n")
    
    # Setup paths (when running without installing the package)
    ise_mcp_server_path = Path(__file__).resolve().parent / "ise_mcp_server"
    if ise_mcp_server_path.exists():
        sys.path.insert(0, str(ise_mcp_server_path.parent))
    
    success = verify_imports()
    
    if success:
        print("\nAll imports verified successfully. The restructured application should work correctly.")
        sys.exit(0)
    else:
        print("\nSome imports failed. Please check the error messages above.")
        sys.exit(1)