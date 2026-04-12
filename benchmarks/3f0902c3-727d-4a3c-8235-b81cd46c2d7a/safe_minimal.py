"""Benign MCP tool: no dangerous sinks."""
from mcp import FastMCP

mcp = FastMCP("safe-minimal")


@mcp.tool()
def echo(text: str) -> str:
    return "echo:" + text
