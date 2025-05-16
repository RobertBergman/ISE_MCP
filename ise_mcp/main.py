import sys
import json
import logging
import asyncio
import argparse
import threading
import time
import requests
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Any, Optional
from functools import partial

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ISEMCPServer")

ISE_BASE = "https://devnetsandboxise.cisco.com"
USERNAME = "readonly"
PASSWORD = "ISEisC00L"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ------------------------------- Load URLs -------------------------------

def load_urls(file_path='urls.json') -> List[Dict[str, str]]:
    with open(file_path, 'r') as f:
        return json.load(f)

URLS = load_urls()

# ------------------------------- Tool Input Schemas -------------------------------

class EmptyInput(BaseModel):
    pass

# ------------------------------- Dynamic Tool Implementations -------------------------------

def make_tool(url: str):
    def tool_impl(_: Dict[str, Any]) -> Dict[str, Any]:
        try:
            full_url = f"{ISE_BASE}{url}"
            logger.info(f"🚀 Fetching data from: {full_url}")
            res = requests.get(full_url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"❌ API error: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    return tool_impl

# ------------------------------- Tool Registry -------------------------------

TOOLS = {
    entry["Name"].replace(" ", "_").lower(): {
        "function": make_tool(entry["URL"]),
        "description": f"Fetch data for {entry['Name']} from Cisco ISE.",
        "input_model": EmptyInput,
    } for entry in URLS
}

# ------------------------------- JSON-RPC Core -------------------------------

def discover_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": name,
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        } for name, tool in TOOLS.items()
    ]

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name not in TOOLS:
        return {"error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    return TOOLS[tool_name]["function"](arguments)

async def process_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "capabilities": {"tools": {"discover": True, "call": True}},
                "serverInfo": {"name": "ISE MCP Server", "version": "1.0.0"},
            },
        }

    if method in ("tools/discover", "tools/list"):
        return {"jsonrpc": "2.0", "id": req_id, "result": discover_tools()}

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        response = call_tool(tool_name, args)

        if "error" in response:
            return {"jsonrpc": "2.0", "id": req_id, "error": response["error"]}

        return {"jsonrpc": "2.0", "id": req_id, "result": response}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}

def send_response(resp: Dict[str, Any]):
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

async def run_server_oneshot():
    input_data = sys.stdin.read().strip()
    request = json.loads(input_data)
    response = await process_request(request)
    if response:
        send_response(response)

# ------------------------------- Entry Point -------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--oneshot", action="store_true")
    args = parser.parse_args()

    if args.oneshot:
        asyncio.run(run_server_oneshot())
