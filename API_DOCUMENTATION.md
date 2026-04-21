"""
API Documentation for MCP Agent Vulnerability Scanner
Complete reference for all available endpoints and usage examples.
"""

# API Endpoints Documentation

## Quick Start

### 1. Setup Environment

```bash
# Using WSL (Windows Subsystem for Linux) or Linux/Mac
wsl  # Enter WSL if on Windows
cd /path/to/taintAnalyzer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.py
```

### 2. Start Server

```bash
uvicorn app.main:app --reload
# Server will be available at http://localhost:8000
```

### 3. Run Tests

```bash
# In a new terminal (with venv activated)
python test_runner.py
```

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/v1/scan/health`

**Description:** Returns scanner status and available features.

**Response:**

```json
{
  "status": "healthy",
  "service": "MCP Taint Analyzer",
  "endpoints": {...},
  "benchmark_agents": [
    "web_scraper",
    "database_query",
    "filesystem",
    "process_execution"
  ]
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/scan/health
```

---

### 2. Scan Single File

**Endpoint:** `POST /api/v1/scan/scan_model`

**Description:** Scan a single Python file for vulnerabilities.

**Request Body:**

```json
{
  "filename": "agent.py",
  "code": "import os\nos.system(user_input)"
}
```

**Response:**

```json
{
  "project_id": "uuid",
  "issues_count": 5,
  "issues_details": [...],
  "summary": {
    "total": 5,
    "high": 2,
    "medium": 2,
    "low": 1
  },
  "pipeline": {
    "mcp_ast": {...},
    "pyre": {...},
    "pysa": {...}
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_model \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.py","code":"import os\nos.system(input())"}'
```

---

### 3. Scan ZIP Archive

**Endpoint:** `POST /api/v1/scan/scan_zip`

**Description:** Upload and scan a ZIP archive containing Python code.

**Request:**

- Content-Type: multipart/form-data
- File parameter: "file" (ZIP file, max 25 MB)

**Response:** Same as scan_model

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_zip \
  -F "file=@project.zip"
```

---

### 4. Scan GitHub Repository

**Endpoint:** `POST /api/v1/scan/scan_github`

**Description:** Scan a GitHub repository for vulnerabilities.

**Request Body:**

```json
{
  "url": "https://github.com/user/repo",
  "github_token": "optional_token_for_private_repos"
}
```

**Response:** Same as scan_model

**Supported URL Formats:**

- `https://github.com/owner/repo`
- `https://github.com/owner/repo/tree/branch_name`
- `https://github.com/owner/repo.git`
- `git@github.com:owner/repo.git`

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/user/repo"}'
```

**With Authentication (Private Repos):**

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{
    "url":"https://github.com/user/private-repo",
    "github_token":"ghp_your_token_here"
  }'
```

---

### 5. Scan Benchmark Agent

**Endpoint:** `GET /api/v1/scan/scan_benchmark/{agent_name}`

**Description:** Run security analysis on a specific benchmark MCP agent.

**Parameters:**

- `agent_name`: One of:
  - `web_scraper` - Web scraping agent with SSRF/command injection
  - `database_query` - Database agent with SQL injection
  - `filesystem` - File system agent with path traversal
  - `process_execution` - Process execution agent with command injection

**Response:** Same as scan_model

**Example:**

```bash
# Scan Web Scraper Agent
curl http://localhost:8000/api/v1/scan/scan_benchmark/web_scraper

# Scan Database Query Agent
curl http://localhost:8000/api/v1/scan/scan_benchmark/database_query

# Scan File System Agent
curl http://localhost:8000/api/v1/scan/scan_benchmark/filesystem

# Scan Process Execution Agent
curl http://localhost:8000/api/v1/scan/scan_benchmark/process_execution
```

---

### 6. Scan All Benchmarks

**Endpoint:** `GET /api/v1/scan/scan_all_benchmarks`

**Description:** Run security analysis on all 4 benchmark MCP agents at once.

**Response:**

```json
{
  "status": "completed",
  "total_agents_scanned": 4,
  "total_issues_found": 45,
  "results": {
    "web_scraper": {...},
    "database_query": {...},
    "filesystem": {...},
    "process_execution": {...}
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/scan/scan_all_benchmarks
```

---

## Benchmark Agents

### Agent 1: WebScraperAgent

**Vulnerabilities:**

- SSRF (Server-Side Request Forgery) - Direct URL access
- Command Injection - Shell execution with unsanitized input
- Insecure Deserialization - Unsafe pickle.load()
- Hardcoded Secrets - API keys in code
- Unsafe File Operations - Direct file path usage

**Tools:**

- `fetch_url(url, timeout)` - SSRF vulnerability
- `parse_html(html, selector)` - Command injection
- `save_cache(key, data)` - Insecure deserialization

---

### Agent 2: DatabaseQueryAgent

**Vulnerabilities:**

- SQL Injection - Direct query execution
- LDAP Injection - Unsanitized filter strings
- Information Disclosure - Detailed error messages
- Path Traversal - Unsafe backup operations
- Hardcoded Credentials - Internal references

**Tools:**

- `execute_query(query, db_name)` - SQL injection
- `authenticate_user(username, password)` - LDAP injection
- `insert_record(table, data)` - Dynamic table names

---

### Agent 3: FileSystemAgent

**Vulnerabilities:**

- Path Traversal / Directory Traversal - No path validation
- Arbitrary File Read/Write/Delete - Unrestricted file operations
- Unsafe Symlink Operations - Can point to sensitive files
- Glob Injection - Pattern parameter not sanitized
- Zip Slip Attack - No extraction path validation

**Tools:**

- `read_file(file_path)` - Path traversal
- `write_file(file_path, content)` - Arbitrary write
- `list_directory(dir_path, pattern)` - Glob injection
- `delete_file(file_path)` - Arbitrary delete

---

### Agent 4: ProcessExecutionAgent

**Vulnerabilities:**

- Command Injection - shell=True enables attacks
- Code Execution - eval() and exec() with user input
- Environment Variable Injection - Secrets in environment
- Argument Injection - Unsafe argument passing
- Shell Injection - Command chaining attacks

**Tools:**

- `execute_command(command)` - Command injection via shell=True
- `run_script(script_path, arguments)` - Path traversal
- `execute_python(code)` - Code execution via exec()
- `batch_execute(commands)` - Multiple injection points

---

## Response Schema

All scan endpoints return responses with this structure:

```json
{
  "project_id": "string",
  "issues_count": "integer",
  "issues_details": [
    {
      "file": "string",
      "line": "integer",
      "type": "string",
      "rule": "string",
      "severity": "HIGH|MEDIUM|LOW",
      "description": "string",
      "fix": "string"
    }
  ],
  "summary": {
    "total": "integer",
    "high": "integer",
    "medium": "integer",
    "low": "integer",
    "pyre_issues": "integer",
    "pysa_issues": "integer",
    "mcp_issues": "integer"
  },
  "pipeline": {
    "mcp_ast": {
      "status": "ok|skipped|failed",
      "issue_count": "integer"
    },
    "pyre": {
      "status": "ok|skipped|failed",
      "issue_count": "integer",
      "debug": {}
    },
    "pysa": {
      "status": "ok|skipped|failed",
      "issue_count": "integer",
      "debug": {}
    }
  },
  "debug": {
    "project_root": "string",
    "upload_folder": "string",
    "pipeline_stages": {}
  }
}
```

---

## Issue Types

### MCP Vulnerabilities (AST-based)

- `SYNTAX_ERROR` - Python syntax errors
- `COMMAND_INJECTION` - OS command execution
- `CODE_INJECTION` - eval/exec usage
- `FILE_SYSTEM_ACCESS` - File operations
- `NETWORK_EXPOSURE` - Socket operations
- `SENSITIVE_DATA_ACCESS` - Environment variable access
- `DESERIALIZATION` - Unsafe deserialization
- `NATIVE_CODE_LOAD` - ctypes usage

### Severity Levels

- `HIGH` - Critical security issue
- `MEDIUM` - Important security issue
- `LOW` - Minor security concern

---

## Examples

### Example 1: Scan a Simple Vulnerable Agent

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_model \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "vulnerable_agent.py",
    "code": "import subprocess\nimport os\n\ndef tool_execute(cmd):\n    os.system(cmd)"
  }'
```

### Example 2: Scan GitHub MCP Project

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/modelcontextprotocol/python-sdk"
  }'
```

### Example 3: Full Benchmark Run

```bash
# Run all benchmarks
curl http://localhost:8000/api/v1/scan/scan_all_benchmarks

# Save results to file
curl http://localhost:8000/api/v1/scan/scan_all_benchmarks > benchmark_results.json
```

---

## Testing

Run the comprehensive test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_runner.py
```

This will:

1. Verify all dependencies are installed
2. Scan all 4 benchmark agents
3. Generate a detailed security report
4. Save results to `reports/` directory

---

## Pipeline Explanation

The scanner runs a 3-stage security analysis pipeline:

### Stage 1: MCP AST Analysis (Fast)

- Pattern-based vulnerability detection
- Syntax validation
- No external tools required
- Runs in ~1 second

### Stage 2: Pyre Type Checking (Optional)

- Static type analysis
- Detects type-related issues
- Requires Pyre binary
- Runs in ~5-10 seconds

### Stage 3: Pysa Taint Analysis (Optional)

- Taint flow analysis
- Source/sink tracing
- Dataflow tracking
- Requires Pyre + models
- Runs in ~10-30 seconds

---

## Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000  # or ss -tuln | grep 8000

# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Pyre not found

```bash
# Pyre should be installed with requirements
pip install pyre-check

# Verify installation
pyre --version
```

### Permission errors

```bash
# Ensure write access to directories
chmod -R 755 ./benchmarks
chmod -R 755 ./reports
```

---

## Performance Notes

- Single file scan: ~1-5 seconds
- ZIP archive (10 files): ~2-10 seconds
- GitHub repository (50 files): ~10-30 seconds
- All benchmarks: ~30-60 seconds
- Large projects (1000+ files): ~5-10 minutes

---

## Security Notes

1. This scanner is for static analysis only
2. Does not execute code (except for safe introspection)
3. GitHub tokens should be kept secret
4. Reports may contain sensitive information
5. Suitable for CI/CD integration

---

## Integration Examples

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Scan with MCP Analyzer
        run: |
          python -m pip install -r requirements.py
          python test_runner.py
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python test_runner.py && exit 0 || exit 1
```

---

## Advanced Configuration

Edit `constants/app_constants.py` to customize:

- Severity levels
- Dangerous sinks
- Benchmark directory
- Reports directory
- Pyre command options

---

## Support

For issues or improvements:

1. Check benchmark agents for examples
2. Review test_runner.py for test patterns
3. Consult pipeline documentation
4. Review Pyre/Pysa documentation

---

"""

# This file serves as comprehensive API documentation

# See the examples and endpoints above for integration guidance
