from fastapi import Request, HTTPException
from core.digital_twin import FinancialDigitalTwin

def get_twin(request: Request) -> FinancialDigitalTwin:
    """Dependency to retrieve the initialized twin."""
    if not request.app.state.twin:
        raise HTTPException(status_code=503, detail="Digital Twin not initialized. Please upload datasets first.")
    return request.app.state.twin
