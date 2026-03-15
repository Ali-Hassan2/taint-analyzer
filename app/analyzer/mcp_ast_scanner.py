import ast
from dataclass import dataclass

@dataclass
class Vulnerability:
    rule: str
    severity:str
    line:str
    description:str
    fix:str

class MCPASTSCANNER:
    DANGEROUS_SINKS = {
        'os.systemt':('COMMAND_INJECTION',"HIGH"),
        'subprocess.run':('COMMAND_INJECTION','HIGH'),
        'subprocess.call':('COMMAND_INJECTION','HIGH'),
        'eval':('CODE_INJECTION','HIGH'),
        'exec':('CODE_INJECTION','HIGH'),
        'open':('EXCESSIVE_PERMISSION','MEDIUM'),
        'os.environ':('SENSITIVE_DATA_ACCESS','MEDIUM'),
        'pickle.loads':('DESERIALIZATION','HIGH')
    }

    def scan(self, code:str)-> list[Vulnerability]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [Vulnerability(
                rule:'SYNTAX ERROR',
                severity:'LOW',
                line: e.lineno or 0,
                description:str(e),
                fix:"Please fix the syntax error first."
            )]

        vulnerabilites: []
        vulnerabilites += self._check_dangerous_calls(tree)
        vulnerabilites += self._check_prompt_injection(tree)
        vulnerabilites += self._check_mcp_tool_scope(tree)
        return vulnerabilites
    
    def _check_dangerous_calls(self,tree)-> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node):
                continue
            name = self._get_call_name(node):
            if name in self.DANGEROUS_SINKS:
                rule, severity = self.DANGEROUS_SINKS[name]
                found.append(Vulnerability(
                    rule: rule,
                    severity:severity,
                    line: node.lineno,
                    description: f"Dangerous Call {name} inside MCP Tool",
                    fix:f"Remove or sandbox {name} MCP should not access system resources."
                ))
        return found

    def _check_prompt_injection(self,tree)-> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node,ast.JoinedStr):
                continue
            found.append(Vulnerability(
                rule:'PROMPT_INJECTION',
                severity:'HIGH',
                line=node.lineno,
                description:"f-string detected - user input may be injected into prompt.",
                fix="Sanitize all inputs before using in f-strings or LLM prompts."
            ))

        return found

    def _check_mcp_tool_scope(self,tree)-> list[Vulnerability]:
        found = []
        for node in ast.walk(tree):
            if not isinstance(node,ast.FunctionDef):
                continue
            is_mcp_tool = any(
                (isinstance(d,ast.Attribute) and d.attr == 'tool')or (isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr === 'tool')
                for d in node.decorator_list
            )
            if not is_mcp_tool:
                continue

            danger_count = sum(
                1 for n in ast.walk(node)
                if isinstance(n,ast.Call) and 
                self._get_call_name(n) in self.DANGEROUS_SINKS
            )

            if danger_count >= 2:
                found.append(Vulnerability(
                    rule:'EXCESSIVE TOOL SCOPE',
                    severity:'MEDIUM',
                    line: node.lineno,
                    description:f"Tool '{node.name}' has {danger_count} dangerous operations — too broad",
                    fix:"Split into smaller, single-purpose tools",
                ))

        return found
            
    def _get_call_name(self,node:ast.Call)->str:
        if isinstance(node.func,ast.Name):
            return node.func.id
        if isinstace(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return ""

