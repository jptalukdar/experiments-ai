from pydantic import BaseModel
from typing import Optional, Any, Dict

class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""
    prompt: str
    session_id: Optional[str] = None # For managing chat history (not used in this example)

class ChatResponse(BaseModel):
    """Response body for the /chat endpoint."""
    response: str
    debug_info: Dict[str, Any]
