"""
FastAPI Router: Chat

Handles direct interactive queries to the Gemma Service, allowing 
users to ask questions about the Digital Twin data.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    query: str
    context_type: str = "global"  # e.g., 'global', 'entity', 'simulation'
    target_id: str = None

@router.post("/")
async def chat_with_twin(request: Request, message: ChatMessage):
    """
    Send a natural language query to the Twin.
    The backend will dynamically construct the prompt block and call Gemma.
    """
    return {"status": "success", "response": "Mock Gemma Chat Response"}
