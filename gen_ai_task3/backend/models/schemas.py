from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user message to the AI assistant.")
    session_id: str = Field(..., min_length=1, max_length=100, description="Unique identifier for the session.")

class SourceMetadata(BaseModel):
    section: str
    text: str
    source: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    tool: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    sources: List[SourceMetadata] = []
