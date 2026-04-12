import logging
import shutil
import subprocess

from fastapi import FastAPI

from app.api.scan import router as scan_router
from constants.app_constants import PROJECT_ROOT

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Taint Analyzer",
    description="Static analysis for MCP-based agents (Pyre, Pysa, AST heuristics)",
    version="1.0.0",
)


@app.on_event("startup")
def start_pyre() -> None:
    pyre_bin = shutil.which("pyre")
    if not pyre_bin:
        for candidate in (
            PROJECT_ROOT / "venv" / "Scripts" / "pyre.exe",
            PROJECT_ROOT / "venv" / "bin" / "pyre",
        ):
            if candidate.is_file():
                pyre_bin = str(candidate)
                break
    if not pyre_bin:
        logger.warning("Pyre not found on PATH or in venv; Pyre/Pysa scans may be skipped.")
        return
    subprocess.run([pyre_bin, "start"], cwd=str(PROJECT_ROOT), check=False)


app.include_router(scan_router, prefix="/api/v1/scan")


@app.get("/")
def root():
    return {"message": "Server is listening.", "status": "ok"}
