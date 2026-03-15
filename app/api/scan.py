from fastapi import APIRouter
from pydantic import BaseModel
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.analyzer.mcp_ast_scanner import MCPASTSCANNER
from app.utils.file_utils import create_project_folder, save_report
from app.utils.pyre_utils import run_pyre
from constants.app_constants import (
    PROJECT_ROOT,
    ISSUE_TYPE_MCP,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class CodeRequest(BaseModel):
    filename: str
    code: str


@router.post("/scan_model")
def scan_model(request: CodeRequest):
    logger.info("Scan request: %s", request.filename)

    project_id, upload_folder, file_path = create_project_folder(
        request.filename, request.code
    )

    pyre_issues, debug = run_pyre(str(PROJECT_ROOT))
    debug.update({
        "project_root": str(PROJECT_ROOT),
        "upload_folder": upload_folder,
        "file_path":     file_path,
    })

    ast_scanner = MCPASTSCANNER()
    mcp_vulnerabilities = ast_scanner.scan(request.code)

    all_issues = pyre_issues + [
        {
            "file":        request.filename,
            "line":        v.line,
            "type":        ISSUE_TYPE_MCP,
            "rule":        v.rule,
            "severity":    v.severity,
            "description": v.description,
            "fix":         v.fix,
        }
        for v in mcp_vulnerabilities
    ]

    save_report(project_id, all_issues)

    return {
        "project_id":   project_id,
        "issues_count": len(all_issues),
        "issues_details":  all_issues,
        "summary": {
            "total":       len(all_issues),
            "high":        sum(1 for v in mcp_vulnerabilities if v.severity == SEVERITY_HIGH),
            "medium":      sum(1 for v in mcp_vulnerabilities if v.severity == SEVERITY_MEDIUM),
            "low":         sum(1 for v in mcp_vulnerabilities if v.severity == SEVERITY_LOW),
            "pyre_issues": len(pyre_issues),
            "mcp_issues":  len(mcp_vulnerabilities),
        },
        "debug": debug,
    }