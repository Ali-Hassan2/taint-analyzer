import subprocess
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from constants.app_constants import PYRE_COMMAND, ISSUE_TYPE_PYRE

logger = logging.getLogger(__name__)


def run_pyre(project_root: str) -> tuple[list, dict]:
    result = subprocess.run(
        PYRE_COMMAND,
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if result.stderr:
        logger.warning("Pyre stderr: %s", result.stderr)

    issues = _parse_pyre_output(result.stdout)
    logger.info("Pyre found %d issues", len(issues))

    debug = {
        "pyre_returncode": result.returncode,
        "pyre_stdout":     result.stdout,
        "pyre_stderr":     result.stderr,
    }

    return issues, debug


def _parse_pyre_output(stdout: str) -> list:
    issues = []
    for line in (stdout or "").splitlines():
        stripped = line.strip()
        if not stripped or ".py:" not in stripped:
            continue
        parts = stripped.split(":", 3)
        if len(parts) < 4:
            continue
        path_part, line_part, _col, message_part = parts
        try:
            line_number = int(line_part)
        except ValueError:
            continue
        issues.append({
            "file":        path_part,
            "line":        line_number,
            "type":        ISSUE_TYPE_PYRE,
            "description": message_part.strip(),
        })
    return issues