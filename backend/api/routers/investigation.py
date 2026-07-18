"""
FastAPI Router: Investigation

Executes deep-dive entity investigations by delegating to InvestigationService.
The service orchestrates the full pipeline:
  Rule Engine → Risk Engine → Evidence Graph → Timeline → PromptBuilder → GemmaService

Every endpoint returns real data. No mocks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_investigation_service, get_twin
from core.digital_twin import FinancialDigitalTwin
from core.investigation_service import InvestigationService

logger = logging.getLogger("verigem.routers.investigation")

router = APIRouter(prefix="/api/investigation", tags=["Investigation"])


# ---------------------------------------------------------------------------
# Entity Investigation
# ---------------------------------------------------------------------------

@router.get(
    "/entity/{entity_id}",
    summary="Run a full-stack investigation on a specific entity",
    response_description=(
        "Risk scores, compliance violations, event timeline, "
        "evidence graph, and Gemma's natural-language explanation."
    ),
)
async def run_entity_investigation(
    entity_id: str,
    svc: InvestigationService = Depends(get_investigation_service),
) -> Dict[str, Any]:
    """
    Execute a complete investigation on any entity in the Digital Twin
    (Vendor, Employee, Purchase Order, Invoice, or Transaction).

    **Pipeline (all deterministic, no LLM involvement until step 7):**
    1. **Rule Engine** — evaluates all compliance rules, filters violations for `entity_id`
    2. **Risk Engine** — fetches risk profile (base + propagated risk)
    3. **Evidence Graph** — builds a React Flow subgraph of all related entities
    4. **Timeline** — retrieves chronological event history for `entity_id`
    5. **Entity Resolution** — fetches Vendor / Employee / PO / Invoice / Transaction data
    6. **Prompt Builder** — assembles a Gemma-optimized investigation prompt
    7. **GemmaService** — generates a natural-language explanation and recommendations

    **Returns:**
    - `entity_id` / `entity_type`
    - `risk` (base, propagated, total)
    - `violations` (rule name, severity, risk score, evidence, affected entities)
    - `violation_count`
    - `timeline` (chronological event list)
    - `evidence_graph` (React Flow nodes + edges)
    - `related_entity_count`
    - `gemma_report` (executive summary, root cause, anomaly explanation, recommendations)
    """
    logger.info("Investigation requested for entity: %s", entity_id)

    try:
        result = svc.investigate_entity(entity_id)
    except KeyError:
        logger.warning("Entity not found in Digital Twin: %s", entity_id)
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{entity_id}' does not exist in the Digital Twin."
        )
    except Exception as exc:
        logger.error(
            "Investigation failed for %s: %s", entity_id, exc, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {str(exc)}"
        )

    return {"status": "success", **result}


# ---------------------------------------------------------------------------
# System-wide anomaly scan
# ---------------------------------------------------------------------------

@router.get(
    "/scan",
    summary="Run Rule Engine across all entities and return summary",
    response_description="All entities with compliance violations, sorted by total risk.",
)
async def scan_all_entities(
    svc: InvestigationService = Depends(get_investigation_service),
    twin: FinancialDigitalTwin = Depends(get_twin),
) -> Dict[str, Any]:
    """
    Run the Rule Engine across the entire Digital Twin store and return
    a prioritised list of entities with violations.

    Useful for building the investigation dashboard / flagged-entities view.
    Does **not** call GemmaService (fast, deterministic only).
    """
    logger.info("System-wide anomaly scan requested.")

    try:
        all_results = svc.rule_engine.evaluate_all(twin.store)
    except Exception as exc:
        logger.error("Anomaly scan failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anomaly scan failed: {str(exc)}")

    # Group violations by affected entity
    entity_summary: Dict[str, Dict[str, Any]] = {}
    for result in all_results:
        for eid in result.affected_entities:
            if eid not in entity_summary:
                risk_profile = svc.risk_engine.get_profile(eid)
                entity_summary[eid] = {
                    "entity_id": eid,
                    "total_risk": risk_profile.total_risk if risk_profile else 0.0,
                    "violations": [],
                }
            entity_summary[eid]["violations"].append({
                "rule_name": result.rule_name,
                "severity": result.severity,
                "risk_score": result.risk_score,
            })

    # Sort by total_risk descending
    flagged = sorted(
        entity_summary.values(),
        key=lambda x: x["total_risk"],
        reverse=True,
    )

    return {
        "status": "success",
        "total_violations": len(all_results),
        "flagged_entities": len(flagged),
        "results": flagged,
    }


# ---------------------------------------------------------------------------
# Single-entity risk lookup (fast — no Gemma)
# ---------------------------------------------------------------------------

@router.get(
    "/risk/{entity_id}",
    summary="Get Risk Engine profile for a specific entity",
)
async def get_entity_risk(
    entity_id: str,
    svc: InvestigationService = Depends(get_investigation_service),
) -> Dict[str, Any]:
    """
    Return the Risk Engine's profile for a single entity.
    Fast endpoint — deterministic only, no GemmaService call.
    """
    profile = svc.risk_engine.get_profile(entity_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"No risk profile found for entity '{entity_id}'."
        )
    return {
        "status": "success",
        "entity_id": profile.entity_id,
        "entity_type": profile.entity_type,
        "base_risk": profile.base_risk,
        "propagated_risk": profile.propagated_risk,
        "total_risk": profile.total_risk,
    }
