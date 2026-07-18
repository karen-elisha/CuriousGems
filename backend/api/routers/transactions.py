"""
FastAPI Router: Transactions
"""
from fastapi import APIRouter, Depends, Request
from api.dependencies import get_twin
from core.digital_twin import FinancialDigitalTwin

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.get("/")
async def list_transactions(
    request: Request, 
    limit: int = 50,
    twin: FinancialDigitalTwin = Depends(get_twin)
):
    """Retrieve a list of real transactions from the Digital Twin DataStore."""
    txns = list(twin.store.transactions.values())
    txns.sort(key=lambda t: t.transaction_date or "", reverse=True)
    
    # Format for frontend table
    data = []
    for t in txns[:limit]:
        data.append({
            "id": t.transaction_id,
            "date": str(t.transaction_date) if t.transaction_date else "N/A",
            "amount": float(t.transaction_amount_inr),
            "status": t.payment_status,
            "vendor": t.vendor_id,
            "approver": t.approver_employee_id,
        })
        
    return {"status": "success", "data": data}

@router.get("/{transaction_id}")
async def get_transaction(request: Request, transaction_id: str):
    """Retrieve a specific transaction."""
    return {"status": "success", "data": {"id": transaction_id}}
