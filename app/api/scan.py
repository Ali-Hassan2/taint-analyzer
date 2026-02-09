from fastapi import APIRouter
from pydantic import BaseModel
import os
import uuid
import json
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CodeRequest(BaseModel):
    filename: str
    code: str


router = APIRouter()


@router.post("/scan_model")
def scan_model(request: CodeRequest):
    logger.info(
        "Received /scan_model request: filename=%s, code_length=%d",
        request.filename,
        len(request.code or ""),
    )

    project_id = str(uuid.uuid4())
    upload_folder = f"benchmarks/{project_id}"
    os.makedirs(upload_folder, exist_ok=True)
    logger.info("Created upload folder: %s (project_id=%s)", upload_folder, project_id)

    file_path = os.path.join(upload_folder, request.filename)
    with open(file_path, "w") as f:
        f.write(request.code)
    logger.info("Wrote code to file: %s", file_path)

    logger.info(
        "Running pyre check from project root=%s using global .pyre_configuration "
        "to analyze benchmarks (including %s)",
        PROJECT_ROOT,
        upload_folder,
    )
    result = subprocess.run(
        # NOTE: The installed `pyre` here does not support `--output` or
        # `--source-directory` flags (see debug output), so we run the plain
        # text checker and parse its stdout ourselves.
        ["pyre", "check"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    logger.info(
        "Pyre finished: returncode=%s, stdout_len=%d, stderr_len=%d",
        result.returncode,
        len(result.stdout or ""),
        len(result.stderr or ""),
    )
    if result.stderr:
        logger.warning("Pyre stderr: %s", result.stderr)

    issues = []
    # The current Pyre version only supports human-readable output; parse it
    # heuristically into structured issues. Typical lines look like:
    # benchmarks/<id>/file.py:line:column: <description...>
    for line in (result.stdout or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Only consider lines that look like file-based error reports.
        # Require at least 3 ':' pieces and a '.py' path prefix.
        if ".py:" not in stripped:
            continue
        parts = stripped.split(":", 3)
        if len(parts) < 4:
            continue
        path_part, line_part, _column_part, message_part = parts
        try:
            line_number = int(line_part)
        except ValueError:
            continue

        issues.append(
            {
                "file": path_part,
                "line": line_number,
                "type": "pyre",
                "description": message_part.strip(),
            }
        )
    logger.info("Parsed %d issues from pyre stdout", len(issues))

    os.makedirs("reports", exist_ok=True)
    reports_path = f"reports/{project_id}.json"
    with open(reports_path, "w") as f:
        json.dump(
            {"project_id": project_id, "issues": issues},
            f,
            indent=2,
        )
    logger.info(
        "Wrote report file: %s (issues_count=%d)", reports_path, len(issues)
    )

    # Include some debug information to help understand Pyre behavior
    response = {
        "project_id": project_id,
        "issues_count": len(issues),
        "issues_dets": issues,
        "debug": {
            "pyre_returncode": result.returncode,
            "pyre_stdout": result.stdout,
            "pyre_stderr": result.stderr,
            "project_root": str(PROJECT_ROOT),
            "upload_folder": upload_folder,
            "file_path": file_path,
        },
    }
    logger.info(
        "Returning response for project_id=%s with issues_count=%d",
        project_id,
        len(issues),
    )
    return response
