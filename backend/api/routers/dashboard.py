"""
FastAPI Router: Dashboard

Handles high-level overview metrics, aggregate compliance scores, 
system-wide risks, and recent timeline events.
"""
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/metrics")
async def get_overview_metrics(request: Request):
    """Retrieve top-level KPIs (Total Spend, High Risk Count, Pending Approvals, etc.)."""
    return {"status": "success", "data": "Mocked metrics data"}

@router.get("/timeline")
async def get_global_timeline(request: Request):
    """Retrieve the recent system-wide event timeline."""
    return {"status": "success", "data": []}
