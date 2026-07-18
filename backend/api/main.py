"""
VeriGem Financial Digital Twin - Main FastAPI Entrypoint
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from core.digital_twin import FinancialDigitalTwin
from .routers import (
    chat_router,
    dashboard_router,
    graph_router,
    investigation_router,
    reports_router,
    simulation_router,
    transactions_router,
    policies_router,
    system_router,
)

app = FastAPI(
    title="VeriGem Financial Digital Twin API",
    description="Backend API for managing the deterministic digital twin and Gemma integration.",
    version="1.0.0"
)

# Global Twin Instance (None until datasets uploaded)
app.state.twin = None

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular routers
app.include_router(system_router)
app.include_router(dashboard_router)
app.include_router(simulation_router)
app.include_router(investigation_router)
app.include_router(graph_router)
app.include_router(chat_router)
app.include_router(reports_router)
app.include_router(transactions_router)
app.include_router(policies_router)

@app.get("/api/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    is_ready = app.state.twin is not None
    return {
        "status": "ok", 
        "service": "verigem-backend", 
        "initialized": is_ready,
        "twin_health": app.state.twin.health() if is_ready else None
    }
