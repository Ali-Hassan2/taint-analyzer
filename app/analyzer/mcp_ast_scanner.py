import ast
import sys
import logging
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from constants.app_constants import (
    DANGEROUS_SINKS,
    SEVERITY_LOW,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
)

logger = logging.getLogger(__name__)

@dataclass
class Vulnerability:
    rule: str
    severity: str
    line: int
    description: str
    fix: str

class MCPASTSCANNER:

    def scan(self, code: str) -> list[Vulnerability]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [Vulnerability(
                rule='SYNTAX_ERROR',
                severity=SEVERITY_LOW,
                line=e.lineno or 0,
                description=str(e),
                fix='Please fix the syntax error first.'
            )]

        vulnerabilities = []
        vulnerabilities += self._check_dangerous_calls(tree)
        vulnerabilities += self._check_prompt_injection(tree)
        vulnerabilities += self._check_mcp_tool_scope(tree)
        return vulnerabilities

    def _check_dangerous_calls(self, tree) -> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = self._get_call_name(node)
            if name in DANGEROUS_SINKS:
                rule, severity = DANGEROUS_SINKS[name]
                found.append(Vulnerability(
                    rule=rule,
                    severity=severity,
                    line=node.lineno,
                    description=f"Dangerous call '{name}' inside MCP tool",
                    fix=f"Remove or sandbox '{name}' — MCP should not access system resources."
                ))
        return found

    def _check_prompt_injection(self, tree) -> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.JoinedStr):
                continue
            found.append(Vulnerability(
                rule='PROMPT_INJECTION',
                severity=SEVERITY_HIGH,
                line=node.lineno,
                description='f-string detected — user input may be injected into prompt.',
                fix='Sanitize all inputs before using in f-strings or LLM prompts.'
            ))
        return found

    def _check_mcp_tool_scope(self, tree) -> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            is_mcp_tool = any(
                (isinstance(d, ast.Attribute) and d.attr == 'tool') or
                (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                 and d.func.attr == 'tool')
                for d in node.decorator_list
            )
            if not is_mcp_tool:
                continue
            danger_count = sum(
                1 for n in ast.walk(node)
                if isinstance(n, ast.Call) and
                self._get_call_name(n) in DANGEROUS_SINKS
            )
            if danger_count >= 2:
                found.append(Vulnerability(
                    rule='EXCESSIVE_TOOL_SCOPE',
                    severity=SEVERITY_MEDIUM,
                    line=node.lineno,
                    description=f"Tool '{node.name}' has {danger_count} dangerous operations — too broad",
                    fix='Split into smaller, single-purpose tools.'
                ))
        return found

    def _get_call_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return ''