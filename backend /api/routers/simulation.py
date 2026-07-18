"""
FastAPI Router: Simulation

Handles What-If branching, running hypothetical actions on the Twin, 
and managing simulation timelines (rollback, reset, compare).
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

class SimulationAction(BaseModel):
    action_type: str
    target_id: str
    parameters: dict = {}

@router.post("/branch")
async def create_branch(request: Request, description: str):
    """Start a new simulation branch."""
    return {"status": "success", "message": f"Branched: {description}"}

@router.post("/execute")
async def execute_action(request: Request, action: SimulationAction):
    """Run an action on the simulated twin (e.g., Block Vendor, Delay Payment)."""
    return {"status": "success", "executed": action.action_type}

@router.post("/rollback")
async def rollback_simulation(request: Request):
    """Undo the last simulation action."""
    return {"status": "success", "message": "Rolled back."}

@router.get("/compare")
async def compare_to_live(request: Request):
    """Get the calculated structural diff between the current simulation and the live twin."""
    return {"status": "success", "diff": {}}
