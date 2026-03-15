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
            if not isinstance(node,ast.Call):
                continue
            name = self._get_call_name(node):
            if name in self.DANGEROUS_SINKS:

