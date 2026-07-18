"""
FastAPI Router: Graph

Handles extracting parts of the Digital Twin graph for the UI.
Outputs React Flow compatible JSON.
"""
from fastapi import APIRouter, Request
from typing import List, Optional

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("/evidence")
async def get_evidence_graph(request: Request, entity_ids: str, depth: int = 1):
    """
    Get the React Flow JSON for an ego-graph surrounding specific entities.
    entity_ids should be a comma-separated list of IDs.
    """
    ids = [e.strip() for e in entity_ids.split(",") if e.strip()]
    return {"status": "success", "nodes": [], "edges": []}

@router.get("/full")
async def get_full_graph(request: Request):
    """Warning: Can be very heavy. Retrieves the entire twin topology."""
    return {"status": "success", "nodes": [], "edges": []}
