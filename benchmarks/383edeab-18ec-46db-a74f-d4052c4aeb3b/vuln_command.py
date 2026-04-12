"""Command injection via os.system in a tool."""
import os

from mcp import FastMCP

mcp = FastMCP("vuln-command")


@mcp.tool()
def run_query(q: str) -> str:
    os.system(q)
    return "done"
