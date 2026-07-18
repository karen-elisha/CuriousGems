from fastapi import APIRouter, Depends, Request
from api.dependencies import get_twin
from core.digital_twin import FinancialDigitalTwin

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/metrics")
async def get_overview_metrics(
    request: Request,
    twin: FinancialDigitalTwin = Depends(get_twin)
):
    """Retrieve test case validation metrics from the live Digital Twin."""
    health = twin.health()
    
    # Run full compliance scan across all rules
    violations = twin.get_compliance_violations()
    
    # Aggregate violations by severity
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0}
    for v in violations:
        sev = v.get("severity", "Medium")
        if sev in severity_counts:
            severity_counts[sev] += 1
            
    # Format a summary chart
    severity_data = [
        {"name": "Critical", "count": severity_counts["Critical"]},
        {"name": "High", "count": severity_counts["High"]},
        {"name": "Medium", "count": severity_counts["Medium"]}
    ]
    
    return {
        "status": "success",
        "data": {
            "total_nodes_analyzed": health["graph_nodes"],
            "total_violations_found": len(violations),
            "high_risk_vendors": len(twin.get_entities("vendor", risk_category="High")),
            "test_status": "Complete",
            "severity_data": severity_data,
            "recent_violations": violations[:5]  # Top 5 violations for the feed
        }
    }
