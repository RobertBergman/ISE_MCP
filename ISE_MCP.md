# ISE MCP Server

## Description
An MCP server providing tools to interact with Cisco Identity Services Engine (ISE).

## Image
```
ise-mcp:latest
```

## Environment Variables
- ISE_URL - The URL of your ISE instance
- ISE_USERNAME - Username for ISE API access
- ISE_PASSWORD - Password for ISE API access

## Tools
This server provides tools for interacting with Cisco ISE, including:

- endpoints - Query ISE endpoints
- identity_groups - Fetch identity groups
- admin_users - Get admin user information
- network_devices - Get network device configurations
- device_admin_policy_sets - Access policy sets
- and many more specialized ISE API tools

## Example Usage
```
Using the endpoints tool, you can retrieve a list of all endpoints registered in ISE.
```

## Related Links
- [Cisco ISE Documentation](https://www.cisco.com/c/en/us/products/security/identity-services-engine/index.html)
