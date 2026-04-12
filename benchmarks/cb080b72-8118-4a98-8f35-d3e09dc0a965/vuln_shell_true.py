"""shell=True subprocess with user-controlled string."""
import subprocess

from mcp import FastMCP

mcp = FastMCP("vuln-shell")


@mcp.tool()
def run_cmd(cmd: str) -> str:
    subprocess.run(cmd, shell=True)
    return "ok"
