"""
FastAPI Router: Policies
"""
from fastapi import APIRouter, Depends, Request
from api.dependencies import get_twin
from core.digital_twin import FinancialDigitalTwin

router = APIRouter(prefix="/api/policies", tags=["Policies"])

@router.get("/")
async def list_policies(
    request: Request, 
    active_only: bool = False,
    twin: FinancialDigitalTwin = Depends(get_twin)
):
    """Retrieve a list of actual compliance policies loaded in the Twin."""
    policies = list(twin.store.compliance_policies.values())
    
    if active_only:
        policies = [p for p in policies if p.status == "Active"]
        
    data = []
    for p in policies:
        data.append({
            "id": p.policy_id,
            "name": p.policy_name,
            "description": p.description,
            "status": p.status,
            "severity": p.severity
        })
        
    return {"status": "success", "data": data}

@router.get("/{policy_id}")
async def get_policy(request: Request, policy_id: str):
    """Retrieve a specific policy."""
    return {"status": "success", "data": {"id": policy_id}}
