from fastapi import FastAPI, UploadFile, File, Form, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
import httpx
import json
from dotenv import load_dotenv
import logging
from datetime import datetime
import uvicorn
from app.api.routes import router as api_router
from app.api.websocket import handle_websocket
from app.core.config import config
from app.services.llm_generator import LLMGenerator
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title=config.APP_NAME,
    description="API for generating LinkedIn posts using Groq",
    version="1.0.0",
    debug=config.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM generator
llm_generator = LLMGenerator()

# In-memory storage for conversations and scheduled posts
conversations: Dict[str, List[dict]] = {}
scheduled_posts: Dict[str, List[dict]] = {}

# Define the input model
class PostData(BaseModel):
    topic: str
    num_posts: int = 3

class PostRequest(BaseModel):
    topic: str
    chat_history: Optional[List[dict]] = None

class PostResponse(BaseModel):
    posts: List[str]
    status: str = "success"
    message: str = "Posts generated successfully"

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_type: str

class Message(BaseModel):
    role: str
    content: str
    timestamp: str = datetime.now().isoformat()

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    posts: Optional[List[str]] = None
    status: str = "success"
    conversation_history: List[dict]

class ScheduleRequest(BaseModel):
    session_id: str
    post_content: str
    schedule_time: str

class ScheduleResponse(BaseModel):
    status: str
    message: str
    scheduled_post: Optional[dict] = None

# Include API routes
app.include_router(api_router, prefix=config.API_V1_STR)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)

@app.post("/generate-posts", response_model=PostResponse, responses={
    500: {"model": ErrorResponse}
})
async def generate_posts(request: PostRequest):
    try:
        logger.info(f"Generating posts for topic: {request.topic}")
        
        # Validate topic
        if not request.topic.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Topic cannot be empty",
                    "error_type": "validation_error"
                }
            )
        
        # Generate posts
        posts = llm_generator.generate_posts(request.topic, request.chat_history)
        
        # Validate posts
        if not posts or len(posts) == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "No posts were generated",
                    "error_type": "generation_error"
                }
            )
        
        logger.info(f"Successfully generated {len(posts)} posts")
        return PostResponse(posts=posts)
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"An error occurred while generating posts: {str(e)}",
                "error_type": "server_error"
            }
        )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/submit/")
async def submit_post(
    post_text: str = Form(...),
    schedule_time: str = Form(...)
):
    return {
        "message": "Post received",
        "post_text": post_text,
        "schedule_time": schedule_time
    }

@app.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    """Process chat messages and generate LinkedIn posts."""
    try:
        # Validate API key
        if not config.GROQ_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Configuration error: GROQ_API_KEY is not set"
            )
            
        # Convert messages to chat history format
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Generate response using LLM
        response_text = await llm_generator.generate_chat_response(chat_history)
        
        # Create response
        return ChatResponse(
            response=response_text,
            posts=[],  # No posts generated in chat mode
            status="success",
            conversation_history=chat_history
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/posts", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def generate_posts(request: ChatRequest):
    """Generate multiple LinkedIn posts based on chat request."""
    try:
        # Validate API key
        if not config.GROQ_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Configuration error: GROQ_API_KEY is not set"
            )
            
        # Convert messages to chat history format
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Get the last user message as the topic
        topic = next(
            (msg.content for msg in reversed(request.messages) if msg.role == "user"),
            "Generate LinkedIn posts"
        )
        
        # Generate posts
        posts, should_post = llm_generator.generate_posts(topic, chat_history)
        
        # Create response
        return ChatResponse(
            response="Generated LinkedIn posts",
            posts=posts,
            status="success",
            conversation_history=chat_history
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating posts: {str(e)}"
        )

@app.post("/schedule-post", response_model=ScheduleResponse)
async def schedule_post(request: ScheduleRequest):
    try:
        # Validate schedule time
        try:
            schedule_time = datetime.fromisoformat(request.schedule_time)
            if schedule_time < datetime.now():
                raise ValueError("Schedule time must be in the future")
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": str(e)
                }
            )
        
        # Store scheduled post
        if request.session_id not in scheduled_posts:
            scheduled_posts[request.session_id] = []
        
        scheduled_post = {
            "content": request.post_content,
            "schedule_time": request.schedule_time,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        scheduled_posts[request.session_id].append(scheduled_post)
        
        return ScheduleResponse(
            status="success",
            message="Post scheduled successfully",
            scheduled_post=scheduled_post
        )
        
    except Exception as e:
        logger.error(f"Error scheduling post: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

@app.get("/scheduled-posts/{session_id}")
async def get_scheduled_posts(session_id: str):
    try:
        if session_id not in scheduled_posts:
            return {"posts": []}
        return {"posts": scheduled_posts[session_id]}
    except Exception as e:
        logger.error(f"Error getting scheduled posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "LinkedIn Post Generator API is running"}

# Run the server when the file is executed directly
if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG
    )
