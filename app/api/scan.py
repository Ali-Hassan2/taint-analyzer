from fastapi import APIRouter

router = APIRouter()

@router.post('/scan_model')
def scan_model():
    return {
        "message":"Scanning model...",
        "status":"ok"
    }
