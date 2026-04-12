import logging
import sys
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.analyzer.scan_pipeline import run_agentic_scan
from app.utils.file_utils import create_project_folder, create_project_from_zip
from constants.app_constants import BENCHMARKS_DIR

logger = logging.getLogger(__name__)
router = APIRouter()


class CodeRequest(BaseModel):
    filename: str
    code: str


@router.post("/scan_model")
def scan_model(request: CodeRequest):
    logger.info("Scan request: %s", request.filename)

    project_id, upload_folder, _file_path = create_project_folder(
        BENCHMARKS_DIR, request.filename, request.code
    )

    return run_agentic_scan(upload_folder, project_id)


@router.post("/scan_project")
def scan_project(request: CodeRequest):
    """
    Upload one file but run multi-file pipeline (Pyre/Pysa on folder + project AST walk).
    Same as /scan_model for a single file; use /scan_zip for archives.
    """
    return scan_model(request)


@router.post("/scan_zip")
async def scan_zip(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="A .zip file is required.")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ZIP file is too large (max 25 MB).")

    try:
        project_id, upload_folder = create_project_from_zip(BENCHMARKS_DIR, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return run_agentic_scan(upload_folder, project_id)
