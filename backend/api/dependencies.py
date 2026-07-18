"""
VeriGem API — Dependency Injection helpers.

All singleton services are booted once in the FastAPI lifespan and stored
on `app.state`. These functions extract them cleanly for use with
FastAPI's `Depends()` system, keeping router code thin and testable.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from core.digital_twin import FinancialDigitalTwin
from core.event_engine import EventEngine
from core.gemma_service import GemmaService
from core.investigation_service import InvestigationService
from core.risk_engine import RiskPropagationEngine
from core.rule_engine import RuleEngine
from core.timeline_manager import TimelineManager


def _require(request: Request, attr: str):
    """Raise a 503 if the requested service hasn't been initialised yet."""
    value = getattr(request.app.state, attr, None)
    if value is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{attr}' is not yet available. The backend may still be booting."
        )
    return value


def get_twin(request: Request) -> FinancialDigitalTwin:
    """Retrieve the FinancialDigitalTwin singleton."""
    return _require(request, "twin")


def get_rule_engine(request: Request) -> RuleEngine:
    """Retrieve the RuleEngine singleton."""
    return _require(request, "rule_engine")


def get_risk_engine(request: Request) -> RiskPropagationEngine:
    """Retrieve the RiskPropagationEngine singleton."""
    return _require(request, "risk_engine")


def get_event_engine(request: Request) -> EventEngine:
    """Retrieve the EventEngine singleton."""
    return _require(request, "event_engine")


def get_timeline_manager(request: Request) -> TimelineManager:
    """Retrieve the TimelineManager singleton."""
    return _require(request, "timeline_manager")


def get_gemma_service(request: Request) -> GemmaService:
    """Retrieve the GemmaService singleton."""
    return _require(request, "gemma_service")


def get_investigation_service(request: Request) -> InvestigationService:
    """Retrieve the InvestigationService singleton."""
    return _require(request, "investigation_service")
