"""Unsafe deserialization in a tool."""
import pickle

from mcp import FastMCP

mcp = FastMCP("vuln-deser")


@mcp.tool()
def load_blob(data: bytes) -> object:
    return pickle.loads(data)
