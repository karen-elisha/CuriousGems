"""
FastAPI Router: System
Handles dataset uploads and twin initialization.
"""
import os
import shutil
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from core.digital_twin import FinancialDigitalTwin

router = APIRouter(prefix="/api/system", tags=["System"])

# Ensure a persistent local directory exists so data survives reloads.
# This answers the user's implicit approval to persist files locally.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload-datasets")
async def upload_datasets(
    request: Request,
    employees: UploadFile = File(...),
    vendors: UploadFile = File(...),
    purchase_orders: UploadFile = File(...),
    invoices: UploadFile = File(...),
    transactions: UploadFile = File(...),
    audit_logs: UploadFile = File(...)
):
    """
    Accepts 6 core CSV files, saves them locally, and boots the Digital Twin.
    """
    files = {
        "employees.csv": employees,
        "vendors.csv": vendors,
        "purchase_orders.csv": purchase_orders,
        "invoices.csv": invoices,
        "transactions.csv": transactions,
        "audit_logs.csv": audit_logs
    }
    
    # Save uploaded files
    try:
        for filename, upload_file in files.items():
            path = os.path.join(DATA_DIR, filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save datasets: {str(e)}")

    # Boot the Twin and attach to global state
    try:
        twin = FinancialDigitalTwin.boot(DATA_DIR)
        request.app.state.twin = twin
        return {"status": "success", "message": "Digital Twin initialized successfully.", "health": twin.health()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize twin from uploaded data: {str(e)}")
