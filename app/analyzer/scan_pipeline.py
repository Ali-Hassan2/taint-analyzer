"""
Agentic scan pipeline: ordered stages (AST heuristics → Pyre → Pysa) for MCP agent code.
All server-side scanning flows through this module.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.utils.file_utils import save_report
from app.utils.pyre_utils import run_pyre, run_pysa
from constants.app_constants import (
    ISSUE_TYPE_MCP,
    PROJECT_ROOT,
    REPORTS_DIR,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
)
from scanner.project_scanner import ProjectScanner

logger = logging.getLogger(__name__)


def _mcp_issues_from_project_scan(upload_root: str, project_id: str) -> list[dict[str, Any]]:
    scanner = ProjectScanner()
    result = scanner.scan_project(upload_root, project_id)
    issues: list[dict[str, Any]] = []
    for fr in result.files:
        for v in fr.vulnerabilities:
            issues.append(
                {
                    "file": fr.relative_path.replace("\\", "/"),
                    "line": v.line,
                    "type": ISSUE_TYPE_MCP,
                    "rule": v.rule,
                    "severity": v.severity,
                    "description": v.description,
                    "fix": v.fix,
                }
            )
    return issues


def run_agentic_scan(upload_folder: str, project_id: str) -> dict[str, Any]:
    """
    Run the full static-analysis pipeline on one extracted upload directory.

    Stages:
      1. mcp_ast — pattern-based rules for MCP tools (fast, no Pyre binary).
      2. pyre — optional type checking (needs pyre.bin).
      3. pysa — optional taint analysis (needs pyre.bin + models in pysa_rules/).
    """
    stages: dict[str, Any] = {}

    mcp_issues = _mcp_issues_from_project_scan(upload_folder, project_id)
    stages["mcp_ast"] = {
        "status": "ok",
        "issue_count": len(mcp_issues),
    }

    pyre_issues, pyre_debug = run_pyre(upload_folder)
    pyre_err = pyre_debug.get("pyre_stderr") or ""
    if pyre_debug.get("pyre_skipped"):
        pyre_status = "skipped"
    elif "Cannot locate" in pyre_err or "Invalid configuration" in pyre_err:
        pyre_status = "failed"
    else:
        pyre_status = "completed"
    stages["pyre"] = {
        "status": pyre_status,
        "issue_count": len(pyre_issues),
        "debug": {
            k: v
            for k, v in pyre_debug.items()
            if k in ("pyre_returncode", "pyre_skipped", "reason", "pyre_cwd")
        },
    }

    pysa_issues, pysa_debug = run_pysa(upload_folder, project_id)
    pysa_err = pysa_debug.get("pysa_stderr") or ""
    if pysa_debug.get("pysa_skipped"):
        pysa_status = "skipped"
    elif "Cannot locate" in pysa_err or "Invalid configuration" in pysa_err:
        pysa_status = "failed"
    else:
        pysa_status = "completed"
    stages["pysa"] = {
        "status": pysa_status,
        "issue_count": len(pysa_issues),
        "debug": {
            k: v
            for k, v in pysa_debug.items()
            if k
            in (
                "pysa_returncode",
                "pysa_skipped",
                "reason",
                "pysa_cwd",
                "pysa_output_dir",
            )
        },
    }

    all_issues = mcp_issues + pyre_issues + pysa_issues

    summary = {
        "total": len(all_issues),
        "high": sum(1 for x in mcp_issues if x.get("severity") == SEVERITY_HIGH),
        "medium": sum(1 for x in mcp_issues if x.get("severity") == SEVERITY_MEDIUM),
        "low": sum(1 for x in mcp_issues if x.get("severity") == SEVERITY_LOW),
        "pyre_issues": len(pyre_issues),
        "pysa_issues": len(pysa_issues),
        "mcp_issues": len(mcp_issues),
    }

    debug = {
        **pyre_debug,
        **pysa_debug,
        "project_root": str(PROJECT_ROOT),
        "upload_folder": upload_folder,
        "pipeline_stages": stages,
    }

    payload = {
        "project_id": project_id,
        "issues": all_issues,
        "summary": summary,
        "pipeline": stages,
        "debug": debug,
    }
    save_report(REPORTS_DIR, project_id, payload)

    return {
        "project_id": project_id,
        "issues_count": len(all_issues),
        "issues_details": all_issues,
        "summary": summary,
        "pipeline": stages,
        "debug": debug,
    }
