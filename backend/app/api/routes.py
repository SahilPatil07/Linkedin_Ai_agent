from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
import logging
from app.models.schemas import (
    ChatRequest, ChatResponse, PostRequest, PostResponse, 
    ErrorResponse, ScheduleRequest, ScheduleResponse
)
from app.services.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)
router = APIRouter()
llm_generator = LLMGenerator()

@router.options("/chat")
async def options_chat():
    """Handle OPTIONS request for chat endpoint."""
    return {}

@router.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    """Process chat messages and generate responses."""
    try:
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        response_text = await llm_generator.generate_chat_response(chat_history)
        
        return ChatResponse(
            response=response_text,
            posts=[],
            conversation_history=chat_history
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "error_type": "server_error"
            }
        )

@router.options("/post")
async def options_post():
    """Handle OPTIONS request for post endpoint."""
    return {}

@router.post("/post", response_model=PostResponse, responses={500: {"model": ErrorResponse}})
async def create_post(request: PostRequest):
    """Create a LinkedIn post."""
    try:
        # Implementation for creating posts
        return PostResponse(
            status="success",
            message="Post created successfully",
            post_id="123"  # Replace with actual post ID
        )
    except Exception as e:
        logger.error(f"Error in post endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "error_type": "server_error"
            }
        )

@router.options("/schedule")
async def options_schedule():
    """Handle OPTIONS request for schedule endpoint."""
    return {}

@router.post("/schedule", response_model=ScheduleResponse, responses={500: {"model": ErrorResponse}})
async def schedule_post(request: ScheduleRequest):
    """Schedule a LinkedIn post."""
    try:
        # Implementation for scheduling posts
        return ScheduleResponse(
            status="success",
            message="Post scheduled successfully",
            schedule_id="456"  # Replace with actual schedule ID
        )
    except Exception as e:
        logger.error(f"Error in schedule endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "error_type": "server_error"
            }
        )

@router.post("/posts", response_model=PostResponse, responses={500: {"model": ErrorResponse}})
async def generate_posts(request: PostRequest) -> PostResponse:
    """Generate multiple LinkedIn posts based on a topic."""
    try:
        # Generate posts using LLM
        posts, should_post = await llm_generator.generate_posts(
            request.topic,
            chat_history=request.chat_history
        )
        
        if not posts:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate posts"
            )
            
        return PostResponse(
            posts=posts,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate posts: {str(e)}"
        )

@router.post("/post-to-linkedin", response_model=PostResponse)
async def post_to_linkedin(request: PostRequest):
    """Generate and post directly to LinkedIn."""
    try:
        # Generate posts
        posts, should_post = await llm_generator.generate_posts(
            request.topic,
            chat_history=request.chat_history
        )
        
        if not posts:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate posts"
            )
            
        # Post the first generated post to LinkedIn
        if should_post and posts:
            result = await llm_generator.post_to_linkedin(posts[0])
            if result["status"] == "error":
                raise HTTPException(
                    status_code=500,
                    detail=result["message"]
                )
            
        return PostResponse(
            posts=posts,
            status="success",
            message="Posts generated and posted to LinkedIn successfully"
        )
        
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post to LinkedIn: {str(e)}"
        ) 