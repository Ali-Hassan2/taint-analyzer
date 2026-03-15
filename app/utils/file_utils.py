import os
import uuid
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from constants.app_constants import BENCHMARKS_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)


def create_project_folder(filename: str, code: str) -> tuple[str, str, str]:
    project_id = str(uuid.uuid4())
    upload_folder = f"{BENCHMARKS_DIR}/{project_id}"
    os.makedirs(upload_folder, exist_ok=True)
    logger.info("Created folder: %s", upload_folder)

    file_path = os.path.join(upload_folder, filename)
    with open(file_path, "w") as f:
        f.write(code)
    logger.info("Wrote code to: %s", file_path)

    return project_id, upload_folder, file_path


def save_report(project_id: str, issues: list) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = f"{REPORTS_DIR}/{project_id}.json"
    with open(report_path, "w") as f:
        json.dump({"project_id": project_id, "issues": issues}, f, indent=2)
    logger.info("Saved report: %s", report_path)
    return report_path