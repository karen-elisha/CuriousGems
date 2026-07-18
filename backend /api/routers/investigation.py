"""
FastAPI Router: Investigation

Handles deep-dive entity analyses, orchestrating the Rule, Risk, 
Timeline, and Gemma engines.
"""
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/investigation", tags=["Investigation"])

@router.get("/entity/{entity_id}")
async def run_entity_investigation(request: Request, entity_id: str):
    """
    Execute a full-stack investigation on a specific entity.
    Returns rules triggered, risk context, subgraph, and Gemma's analysis.
    """
    # Actual implementation would resolve InvestigationService from request.app.state
    return {"status": "success", "entity_id": entity_id, "report": "Mock investigation result"}
