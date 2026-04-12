"""SSRF-style pattern: tool param as URL."""
import requests
from mcp import FastMCP

mcp = FastMCP("vuln-ssrf")


@mcp.tool()
def fetch_url(url: str) -> str:
    r = requests.get(url)
    return r.text[:200]
