"""
VeriGem Financial Digital Twin - Main FastAPI Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    chat_router,
    dashboard_router,
    graph_router,
    investigation_router,
    reports_router,
    simulation_router,
)

app = FastAPI(
    title="VeriGem Financial Digital Twin API",
    description="Backend API for managing the deterministic digital twin and Gemma integration.",
    version="1.0.0"
)

# Setup CORS for the upcoming frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
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

@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "verigem-backend"}
