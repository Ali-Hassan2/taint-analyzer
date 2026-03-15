from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_DIR = "benchmarks"
REPORTS_DIR = "reports"

PYRE_COMMAND = ["pyre", "check"]

SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"

ISSUE_TYPE_PYRE = "pyre"
ISSUE_TYPE_MCP = "mcp_vulnerability"

DANGEROUS_SINKS = {
    'os.system':       ('COMMAND_INJECTION',     'HIGH'),
    'subprocess.run':  ('COMMAND_INJECTION',     'HIGH'),
    'subprocess.call': ('COMMAND_INJECTION',     'HIGH'),
    'eval':            ('CODE_INJECTION',        'HIGH'),
    'exec':            ('CODE_INJECTION',        'HIGH'),
    'open':            ('EXCESSIVE_PERMISSION',  'MEDIUM'),
    'os.environ':      ('SENSITIVE_DATA_ACCESS', 'MEDIUM'),
    'pickle.loads':    ('DESERIALIZATION',       'HIGH'),
}

MCP_TOOL_DECORATORS = ['tool']