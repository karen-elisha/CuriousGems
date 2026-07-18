"""
VeriGem Financial Digital Twin - Main FastAPI Entrypoint
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core.digital_twin import FinancialDigitalTwin
from core.event_engine import EventEngine
from core.gemma_service import GemmaService
from core.investigation_service import InvestigationService
from core.risk_engine import RiskPropagationEngine
from core.rule_engine import RuleEngine
from core.timeline_manager import TimelineManager

from .routers import (
    chat_router,
    dashboard_router,
    graph_router,
    investigation_router,
    policies_router,
    reports_router,
    simulation_router,
    system_router,
    transactions_router,
)

logger = logging.getLogger("verigem.api")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Boot the Financial Digital Twin and all singleton backend engines.
    Engines are stored on app.state so every router can access them
    via the dependency injection helpers in api/dependencies.py.
    """
    logger.info("═" * 60)
    logger.info("  VeriGem API — Boot Sequence Starting")
    logger.info("═" * 60)

    # 1. Locate datasets
    backend_dir = Path(__file__).resolve().parent.parent
    datasets_dir = backend_dir / "datasets" / "VeriGem_Datasets"
    if not datasets_dir.is_dir():
        logger.critical("Datasets directory not found: %s", datasets_dir)
        raise FileNotFoundError(f"Datasets directory not found: {datasets_dir}")

    # 2. Boot the Digital Twin (loads all CSVs + builds graph)
    logger.info("Booting Financial Digital Twin from: %s", datasets_dir)
    twin = FinancialDigitalTwin.boot(str(datasets_dir))

    # 3. Instantiate the deterministic engines
    rule_engine = RuleEngine()
    risk_engine = RiskPropagationEngine(twin.store)
    event_engine = EventEngine()
    timeline_manager = TimelineManager(twin)

    # 4. Instantiate the Gemma AI service (singleton — client created once)
    gemma_service = GemmaService()

    # 5. Instantiate the orchestrating investigation service
    investigation_service = InvestigationService(
        twin=twin,
        rule_engine=rule_engine,
        risk_engine=risk_engine,
        event_engine=event_engine,
        timeline_manager=timeline_manager,
        gemma_service=gemma_service,
    )

    # 6. Attach every singleton to application state
    app.state.twin = twin
    app.state.rule_engine = rule_engine
    app.state.risk_engine = risk_engine
    app.state.event_engine = event_engine
    app.state.timeline_manager = timeline_manager
    app.state.gemma_service = gemma_service
    app.state.investigation_service = investigation_service

    health = twin.health()
    logger.info("Digital Twin ready — %d entities, %d nodes, %d edges",
                health["total_entities"], health["graph_nodes"], health["graph_edges"])
    logger.info("GemmaService mode: %s", "MOCK" if gemma_service.is_mock else "LIVE")
    logger.info("═" * 60)
    logger.info("  VeriGem API is OPERATIONAL")
    logger.info("═" * 60)

    yield

    logger.info("VeriGem API shutting down cleanly.")


app = FastAPI(
    title="VeriGem Financial Digital Twin API",
    description=(
        "Backend API for the VeriGem Financial Digital Twin. "
        "Exposes deterministic Rule/Risk/Graph engines augmented by "
        "Google Gemma (google/gemma-3-27b-it) for natural language analysis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all modular routers
app.include_router(dashboard_router)
app.include_router(simulation_router)
app.include_router(investigation_router)
app.include_router(graph_router)
app.include_router(chat_router)
app.include_router(reports_router)
app.include_router(transactions_router)
app.include_router(policies_router)
app.include_router(system_router)


@app.get("/health", tags=["System"])
async def health_check(request: Request):
    """Simple health check endpoint."""
    initialized = hasattr(request.app.state, "twin") and request.app.state.twin is not None
    return {"status": "ok", "service": "verigem-backend", "initialized": initialized}
