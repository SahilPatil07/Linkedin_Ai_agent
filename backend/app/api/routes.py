from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from app.models.schemas import ChatRequest, ChatResponse, PostRequest, PostResponse, ErrorResponse
from app.services.llm_generator import LLMGenerator
from app.services.chat_processor import ChatProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request and generate a response."""
    try:
        # Convert messages to chat history format
        chat_history = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Generate response using LLM
        llm = LLMGenerator()
        response = await llm.generate_chat_response(chat_history)
        
        # Process the response
        processor = ChatProcessor()
        response_text, should_post, post_content = processor.process_response(
            response,
            request.messages[-1].content if request.messages else ""
        )
        
        # Extract any posts from the response
        posts = processor.extract_posts(response)
        
        return ChatResponse(
            response=response_text,
            posts=posts,
            status="success",
            conversation_history=chat_history
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

@router.post("/posts", response_model=PostResponse, responses={500: {"model": ErrorResponse}})
async def generate_posts(request: PostRequest) -> PostResponse:
    """Generate multiple LinkedIn posts based on a topic."""
    try:
        # Convert messages to chat history format
        chat_history = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Generate posts using LLM
        llm = LLMGenerator()
        posts, success = await llm.generate_posts_async(
            request.topic,
            chat_history=chat_history
        )
        
        if not success:
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