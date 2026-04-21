"""
SETUP AND QUICK START GUIDE
MCP Agent Vulnerability Scanner - Complete Installation and Usage Guide

This guide walks you through setting up and running the complete vulnerability
scanner system for MCP-based AI agents.
"""

# =============================================================================

# COMPLETE SETUP GUIDE

# =============================================================================

## Prerequisites

- Windows, macOS, or Linux
- WSL (Windows Subsystem for Linux) if on Windows
- Python 3.8+
- Git (optional, for GitHub repo cloning)
- 2GB+ free disk space

## Directory Structure

````
taintAnalyzer/
├── app/
│   ├── agents/                    # NEW: 4 Benchmark MCP Agents
│   │   ├── agent_base.py         # Base class for all agents
│   │   ├── benchmark_1_web_scraper.py       # SSRF, Command Injection
│   │   ├── benchmark_2_db_query.py          # SQL Injection, LDAP Injection
│   │   ├── benchmark_3_filesystem.py        # Path Traversal, Zip Slip
│   │   ├── benchmark_4_process_exec.py      # Code Execution, Shell Injection
│   │   └── __init__.py
│   ├── api/
│   │   └── scan.py                # UPDATED: New endpoints
│   ├── analyzer/
│   │   ├── scan_pipeline.py
│   │   ├── mcp_ast_scanner.py
│   │   ├── pyre_runner.py
│   │   ├── taint_parser.py
│   │   └── rules.py
│   ├── benchmarks_testers/
│   │   ├── agent_benchmark.py     # NEW: Comprehensive test suite
│   │   └── __init__.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   ├── pyre_utils.py
│   │   └── github_utils.py        # NEW: GitHub repo support
│   ├── config/
│   ├── main.py                    # FastAPI app
│   └── __init__.py
├── constants/
│   └── app_constants.py
├── scanner/
│   ├── project_scanner.py
│   └── __init__.py
├── pysa_rules/                    # Taint analysis rules
│   ├── mcp_agent.pysa
│   ├── mcp_sanitizers.pysa
│   ├── mcp_sinks.pysa
│   ├── mcp_sources.pysa
│   ├── taint.config
│   └── stubs/
├── benchmarks/                    # Scan results stored here
├── reports/                       # Reports generated here
├── test_runner.py                 # NEW: Test script
├── requirements.py                # Dependencies
├── API_DOCUMENTATION.md           # NEW: API docs
├── SETUP_GUIDE.md                # This file
└── README.md                      # Project README

## Step-by-Step Installation

### Step 1: Enter WSL (Windows Users)
```bash
# On Windows, open PowerShell and type:
wsl

# You should see a Linux shell prompt (usually $)
cd /home/your-username  # or navigate to your project
````

### Step 2: Navigate to Project

```bash
cd ~/path/to/taintAnalyzer
# or
cd /mnt/c/Users/YourUser/Documents/taintAnalyzer  # If on Windows
```

### Step 3: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.py

# Verify Pyre installation
pyre --version
```

### Step 5: Start the Server

```bash
# Make sure venv is activated
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload

# Output should show:
# Uvicorn running on http://127.0.0.1:8000
#
# Press CTRL+C to stop
```

### Step 6: Test the Scanner (New Terminal)

```bash
# Open a new terminal
# WSL: wsl (if needed)
# cd to project folder
cd ~/path/to/taintAnalyzer

# Activate venv
source venv/bin/activate

# Run tests
python test_runner.py
```

## Usage Examples

### Example 1: Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/scan/health
```

### Example 2: Scan a Single Vulnerable File

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_model \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_agent.py",
    "code": "import os\nos.system(input())"
  }'
```

### Example 3: Scan WebScraperAgent Benchmark

```bash
curl http://localhost:8000/api/v1/scan/scan_benchmark/web_scraper
```

### Example 4: Scan All 4 Benchmarks

```bash
curl http://localhost:8000/api/v1/scan/scan_all_benchmarks
```

### Example 5: Scan GitHub Repository

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/mcp-agent-repo"
  }'
```

## What's New in This Version

### 1. Four Complete Benchmark Agents

All agents have realistic vulnerabilities built in for testing:

**WebScraperAgent** (benchmark_1_web_scraper.py)

- SSRF vulnerability in fetch_url()
- Command injection in parse_html()
- Insecure pickle deserialization
- Hardcoded API keys
- 350+ lines of code

**DatabaseQueryAgent** (benchmark_2_db_query.py)

- SQL injection in execute_query()
- LDAP injection in authenticate_user()
- Information disclosure via error messages
- Path traversal in backups
- 330+ lines of code

**FileSystemAgent** (benchmark_3_filesystem.py)

- Path traversal in read_file()
- Directory traversal in write_file()
- Glob injection in list_directory()
- Zip slip attack in extract_zip()
- 300+ lines of code

**ProcessExecutionAgent** (benchmark_4_process_exec.py)

- Command injection via shell=True
- Code execution with eval/exec()
- Environment variable injection
- Argument injection attacks
- 320+ lines of code

### 2. GitHub Repository Support

New endpoint to scan any GitHub repository:

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/owner/repo"}'
```

Supports:

- Public and private repositories
- GitHub authentication tokens
- Shallow cloning for performance
- ZIP download fallback

### 3. Comprehensive Test Suite

Run `python test_runner.py` to:

- Scan all 4 benchmark agents
- Generate detailed security reports
- Verify scanner functionality
- Save results to reports/

### 4. Enhanced API Endpoints

New endpoints in /api/v1/scan/:

- `POST /scan_github` - Scan GitHub repos
- `GET /scan_benchmark/{agent}` - Scan specific agent
- `GET /scan_all_benchmarks` - Scan all 4 at once
- `GET /health` - Health check with feature list

## Running Your First Scan

### Quick Start (5 minutes)

```bash
# 1. Start server
source venv/bin/activate
uvicorn app.main:app --reload

# 2. In another terminal, run tests
source venv/bin/activate
python test_runner.py

# 3. Check reports/
cat reports/benchmark_*.json
```

### Full Benchmark (10-15 minutes)

```bash
curl http://localhost:8000/api/v1/scan/scan_all_benchmarks > results.json

# View results
cat results.json | python -m json.tool
```

### Scan Your Own Repository

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_github \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/your-org/your-agent-repo"}'
```

## Understanding Results

The scanner returns issues with:

- **file**: Where the issue is
- **line**: Line number in the code
- **severity**: HIGH, MEDIUM, or LOW
- **rule**: Type of vulnerability
- **description**: What was found
- **fix**: How to fix it

Example issue:

```json
{
  "file": "agent.py",
  "line": 42,
  "type": "mcp_vulnerability",
  "rule": "COMMAND_INJECTION",
  "severity": "HIGH",
  "description": "User input passed to os.system()",
  "fix": "Use subprocess.run() with a list of arguments"
}
```

## Troubleshooting

### 1. Python not found

```bash
# WSL: Use python3 instead of python
python3 --version
python3 -m venv venv
```

### 2. venv not working

```bash
# Deactivate first
deactivate

# Recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### 3. Port 8000 already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### 4. Pyre not found

```bash
# Reinstall
pip uninstall pyre-check
pip install pyre-check

# Verify
pyre --version
```

### 5. Permission denied

```bash
# Fix directory permissions
chmod -R 755 benchmarks/
chmod -R 755 reports/
chmod +x test_runner.py
```

## Advanced Usage

### Custom Agent Scanning

Save your agent code as agent.py:

```bash
curl -X POST http://localhost:8000/api/v1/scan/scan_model \
  -H "Content-Type: application/json" \
  -d @agent.json
```

### Batch Testing

```bash
# Scan multiple repos
for repo in org/repo1 org/repo2 org/repo3; do
  curl -X POST http://localhost:8000/api/v1/scan/scan_github \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"https://github.com/$repo\"}"
done
```

### CI/CD Integration

The scanner can integrate with:

- GitHub Actions
- GitLab CI/CD
- Jenkins
- CircleCI
- Any CI/CD system that can call HTTP APIs

Example GitHub Actions workflow:

```yaml
name: Security Scan
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Security Scan
        run: python test_runner.py
```

## File Count Summary

Total new files created:

- `app/agents/agent_base.py` - Base class (40 lines)
- `app/agents/benchmark_1_web_scraper.py` - Agent 1 (190 lines)
- `app/agents/benchmark_2_db_query.py` - Agent 2 (200 lines)
- `app/agents/benchmark_3_filesystem.py` - Agent 3 (200 lines)
- `app/agents/benchmark_4_process_exec.py` - Agent 4 (210 lines)
- `app/agents/__init__.py` - Module init (20 lines)
- `app/utils/github_utils.py` - GitHub support (280 lines)
- `app/benchmarks_testers/agent_benchmark.py` - Test suite (280 lines)
- `app/benchmarks_testers/__init__.py` - Module init (5 lines)
- `test_runner.py` - Test runner (200 lines)
- `API_DOCUMENTATION.md` - API docs (500+ lines)
- `SETUP_GUIDE.md` - This guide (600+ lines)

**Total: ~2,500 lines of new code**

Updated files:

- `app/api/scan.py` - Added GitHub + benchmark endpoints
- `requirements.py` - Added requests + pydantic

## Next Steps

1. **Start the server** - `uvicorn app.main:app --reload`
2. **Run tests** - `python test_runner.py`
3. **Explore benchmarks** - Curl the benchmark endpoints
4. **Scan your code** - Use `/scan_model` or `/scan_github`
5. **Check reports** - Results saved to `reports/`

## Additional Resources

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Project README**: See `README.md`
- **Benchmark Agents**: Located in `app/agents/`
- **Test Suite**: Located in `app/benchmarks_testers/`
- **Test Runner**: Run `python test_runner.py`

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Review logs in `reports/` directory
3. Ensure venv is activated
4. Verify Python version (3.8+)
5. Check port 8000 is available

## Timeline

- **Setup & installation**: 5-10 minutes
- **First scan**: 1-2 minutes
- **Full benchmark run**: 10-15 minutes
- **Integration testing**: 5 minutes

Total initial setup time: **20-30 minutes**

---

Ready to scan? Start with:

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Then in another terminal:

```bash
python test_runner.py
```

Good luck! 🚀
"""

# This file provides complete setup and installation guidance
