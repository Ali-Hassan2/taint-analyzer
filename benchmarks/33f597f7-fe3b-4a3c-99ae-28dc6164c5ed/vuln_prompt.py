"""f-string interpolates tool argument (prompt-injection style)."""
from mcp import FastMCP

mcp = FastMCP("vuln-prompt")


@mcp.tool()
def build_prompt(user_text: str) -> str:
    return f"System: you are helpful. User: {user_text}"
