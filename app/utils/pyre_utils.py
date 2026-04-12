import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from constants.app_constants import ISSUE_TYPE_PYRE, ISSUE_TYPE_PYSA

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_pyre_binary() -> str | None:
    exe = shutil.which("pyre")
    if exe:
        return exe
    for candidate in (
        _PROJECT_ROOT / "venv" / "Scripts" / "pyre.exe",
        _PROJECT_ROOT / "venv" / "bin" / "pyre",
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def run_pyre(cwd: str) -> tuple[list, dict]:
    pyre_bin = _resolve_pyre_binary()
    if not pyre_bin:
        logger.warning("Pyre binary not found; skipping type check.")
        return [], {"pyre_skipped": True, "reason": "pyre binary not found"}

    safe_cwd = str(Path(cwd).resolve())
    cmd = [pyre_bin, "check"]
    result = subprocess.run(cmd, cwd=safe_cwd, capture_output=True, text=True)

    if result.stderr:
        logger.warning("Pyre stderr: %s", result.stderr)

    issues = _parse_pyre_output(result.stdout)
    logger.info("Pyre found %d issues", len(issues))

    debug = {
        "pyre_returncode": result.returncode,
        "pyre_stdout": result.stdout,
        "pyre_stderr": result.stderr,
        "pyre_cwd": safe_cwd,
    }
    return issues, debug


def run_pysa(cwd: str, project_id: str) -> tuple[list, dict]:
    pyre_bin = _resolve_pyre_binary()
    if not pyre_bin:
        logger.warning("Pyre binary not found; skipping Pysa.")
        return [], {"pysa_skipped": True, "reason": "pyre binary not found"}

    safe_cwd = str(Path(cwd).resolve())
    out_dir = (_PROJECT_ROOT / "reports" / "pysa_runs" / project_id).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        pyre_bin,
        "analyze",
        "--output-format",
        "json",
        "--save-results-to",
        str(out_dir),
        "--no-verify",
    ]
    result = subprocess.run(cmd, cwd=safe_cwd, capture_output=True, text=True)

    if result.stderr:
        logger.warning("Pysa stderr: %s", result.stderr)

    issues = _load_pysa_issues(out_dir)
    logger.info("Pysa found %d issues", len(issues))

    debug = {
        "pysa_returncode": result.returncode,
        "pysa_stdout": result.stdout,
        "pysa_stderr": result.stderr,
        "pysa_cwd": safe_cwd,
        "pysa_output_dir": str(out_dir),
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
        issues.append(
            {
                "file": path_part.replace("\\", "/"),
                "line": line_number,
                "type": ISSUE_TYPE_PYRE,
                "description": message_part.strip(),
            }
        )
    return issues


def _load_pysa_issues(out_dir: Path) -> list:
    path = out_dir / "taint-output.json"
    if not path.is_file():
        for p in out_dir.glob("*.json"):
            path = p
            break
        else:
            return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read Pysa JSON %s: %s", path, e)
        return []
    return _parse_pysa_json(data)


def _parse_pysa_json(data) -> list:
    if isinstance(data, dict):
        if "errors" in data:
            data = data["errors"]
        elif "issues" in data:
            data = data["issues"]
        elif "results" in data:
            data = data["results"]
        else:
            data = [data]

    if not isinstance(data, list):
        return []

    issues: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        loc = item.get("location") or {}
        path = (
            item.get("path")
            or item.get("filename")
            or item.get("file")
            or loc.get("path")
            or loc.get("filename")
        )
        line = item.get("line") or item.get("line_number") or loc.get("line")
        if path is None or line is None:
            continue
        try:
            line_int = int(line)
        except (TypeError, ValueError):
            continue
        name = item.get("name") or item.get("rule") or item.get("code") or "taint_flow"
        desc = (
            item.get("description")
            or item.get("message")
            or item.get("concise_description")
            or item.get("long_description")
            or str(name)
        )
        issues.append(
            {
                "file": str(path).replace("\\", "/"),
                "line": line_int,
                "type": ISSUE_TYPE_PYSA,
                "rule": str(name),
                "description": str(desc).strip(),
            }
        )
    return issues
