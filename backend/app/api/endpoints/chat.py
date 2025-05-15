from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ...services.chat import ChatService
from ...schemas.chat import ChatRequest, ChatResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Handle chat requests and return responses.
    """
    try:
        chat_service = ChatService()
        response = await chat_service.get_chat_response(
            message=request.message,
            chat_history=request.chat_history
        )
        
        if not response:
            raise HTTPException(status_code=500, detail="No response from chat service")
            
        return ChatResponse(
            status=response.get("status", "error"),
            message=response.get("message", ""),
            error=response.get("error", ""),
            is_post=response.get("is_post", False)
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        ) 