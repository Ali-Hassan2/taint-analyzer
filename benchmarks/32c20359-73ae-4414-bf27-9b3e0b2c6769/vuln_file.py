"""User path flows to open() inside a tool."""
from mcp import FastMCP

mcp = FastMCP("vuln-file")


@mcp.tool()
def read_user_file(path: str) -> str:
    with open(path) as f:
        return f.read()
