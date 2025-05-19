from setuptools import setup, find_packages

setup(
    name="ise_mcp_server",
    version="0.1.0",
    description="MCP server for Cisco ISE",
    author="Anthropic",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        'ise_mcp_server.config': ['*.json'],
    },
    install_requires=[
        "pydantic",
        "python-dotenv",
        "fastmcp",
        "httpx",
        "aiocache",
        "aiolimiter",
    ],
    entry_points={
        'console_scripts': [
            'ise-mcp-server=ise_mcp_server.__main__:main',
        ],
    },
    python_requires='>=3.8',
)