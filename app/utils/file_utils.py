import io
import json
import logging
import os
import uuid
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolved at import: app/utils -> project root (taintAnalyzer)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_pyre_config_for_upload(upload_folder: str) -> None:
    upload = Path(upload_folder).resolve()
    cfg = {
        "site_package_search_strategy": "pep561",
        "source_directories": ["."],
        "exclude": [r"^\.pyre/.*", r"^__pycache__/.*", r"^\.venv/.*", r"^venv/.*"],
        "search_path": [str(_PROJECT_ROOT / "pysa_rules" / "stubs")],
        "taint_models_path": [str(_PROJECT_ROOT / "pysa_rules")],
        "strict": False,
    }
    pyre_binary = os.environ.get("PYRE_BINARY", "").strip()
    if pyre_binary:
        cfg["binary"] = pyre_binary
    (upload / ".pyre_configuration").write_text(
        json.dumps(cfg, indent=2), encoding="utf-8"
    )
    logger.info("Wrote Pyre config in %s", upload)


def create_project_folder(
    benchmarks_dir: str, filename: str, code: str
) -> tuple[str, str, str]:
    project_id = str(uuid.uuid4())
    upload_folder = f"{benchmarks_dir}/{project_id}"
    os.makedirs(upload_folder, exist_ok=True)
    logger.info("Created folder: %s", upload_folder)

    file_path = os.path.join(upload_folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    logger.info("Wrote code to: %s", file_path)

    _write_pyre_config_for_upload(upload_folder)
    return project_id, upload_folder, file_path


def create_project_from_zip(
    benchmarks_dir: str, content: bytes, max_uncompressed_bytes: int = 30 * 1024 * 1024
) -> tuple[str, str]:
    project_id = str(uuid.uuid4())
    upload_folder = Path(benchmarks_dir) / project_id
    upload_folder.mkdir(parents=True, exist_ok=True)
    base = upload_folder.resolve()

    total_uncompressed = 0
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"Unsafe zip path: {name!r}")
            target = (base / name).resolve()
            try:
                target.relative_to(base)
            except ValueError as e:
                raise ValueError(f"Zip slip attempt: {name!r}") from e

            total_uncompressed += info.file_size
            if total_uncompressed > max_uncompressed_bytes:
                raise ValueError("ZIP uncompressed size exceeds limit")

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, open(target, "wb") as out:
                chunk = src.read(1024 * 1024)
                while chunk:
                    out.write(chunk)
                    chunk = src.read(1024 * 1024)

    upload_str = str(upload_folder)
    _write_pyre_config_for_upload(upload_str)
    logger.info("Extracted ZIP to %s", upload_str)
    return project_id, upload_str


def save_report(reports_dir: str, project_id: str, payload: dict) -> str:
    os.makedirs(reports_dir, exist_ok=True)
    report_path = f"{reports_dir}/{project_id}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logger.info("Saved report: %s", report_path)
    return report_path
