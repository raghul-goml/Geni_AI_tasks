import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.config import HANDBOOK_PATH
from backend.logging_config import logger
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agent.agent import CampusAgent

app = FastAPI(title="CampusAI API", version="1.0.0")

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize single agent
agent = CampusAgent()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "campus-ai"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    # Input Guardrails / Validations
    if not request.message.strip():
        logger.warning(f"guardrail_violation | reason=empty_message | session_id={request.session_id}")
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    if len(request.message) > 2000:
        logger.warning(f"guardrail_violation | reason=message_too_long | session_id={request.session_id}")
        raise HTTPException(status_code=400, detail="Message exceeds maximum limit of 2000 characters.")
        
    if len(request.session_id) > 100 or len(request.session_id) < 1:
        logger.warning(f"guardrail_violation | reason=invalid_session_id | session_id={request.session_id}")
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    try:
        logger.info(f"request_received | session_id={request.session_id}")
        
        result = agent.process_message(request.message, request.session_id)
        
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(f"request_completed | session_id={request.session_id} | latency_ms={latency_ms}")
        
        return ChatResponse(
            answer=result["answer"],
            tool=result.get("tool"),
            action=result.get("action"),
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        logger.error(f"internal_server_error | session_id={request.session_id} | error_type={type(e).__name__} | message={str(e)}")
        # Mask exception details from users
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the request right now."
        )

@app.get("/downloads/university_handbook.pdf")
def download_handbook_endpoint():
    pdf_path = Path(HANDBOOK_PATH)
    if not pdf_path.exists():
        logger.error(f"file_not_found | path={HANDBOOK_PATH}")
        raise HTTPException(status_code=404, detail="University handbook PDF is not available.")
        
    return FileResponse(
        path=pdf_path,
        filename="university_handbook.pdf",
        media_type="application/pdf"
    )
