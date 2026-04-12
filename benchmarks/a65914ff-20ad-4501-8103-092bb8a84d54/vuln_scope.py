"""Multiple dangerous operations in one tool (excessive scope)."""
import os
import subprocess

from mcp import FastMCP

mcp = FastMCP("vuln-scope")


@mcp.tool()
def mega_tool(cmd: str, path: str) -> str:
    os.system(cmd)
    subprocess.run(["echo", "x"], check=False)
    with open(path) as f:
        return f.read()
