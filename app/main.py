from fastapi import FastAPI
from app.api.scan import router as scan_router


app = FastAPI(
    title="MCP Taint Analyzer",
    description="Static taint-based vulnerability analyzer using Pyre/Pysa",
    version="1.0.0"
)

app.include_router(scan_router,prefix="/api/v1/scan")

@app.get("/")
def root():
    return {
        "message":"Server is Listening..",
        "status":"ok"
    }