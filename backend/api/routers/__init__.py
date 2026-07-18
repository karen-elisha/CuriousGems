"""
FastAPI Routers Package.
"""
from .chat import router as chat_router
from .dashboard import router as dashboard_router
from .graph import router as graph_router
from .investigation import router as investigation_router
from .reports import router as reports_router
from .simulation import router as simulation_router
from .transactions import router as transactions_router
from .policies import router as policies_router

__all__ = [
    "dashboard_router",
    "simulation_router",
    "investigation_router",
    "graph_router",
    "chat_router",
    "reports_router",
    "transactions_router",
    "policies_router",
]
