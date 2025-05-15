from fastapi import FastAPI, UploadFile, File, Form, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from app.core.config import settings
from app.services.llm_generator import LLMGenerator
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse

# Import core components
from app.db.session import engine
from app.db import models

# Import API routers
from app.api.endpoints import auth, users, generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="API backend for LinkedIn Post Generator using LLM",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600
    )

    # Global error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions."""
        logger.error(f"Global error handler caught: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An unexpected error occurred",
                "error_type": "server_error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # Startup event handler
    @app.on_event("startup")
    async def startup_event():
        """Initialize database and other startup tasks."""
        try:
            # Create database tables
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Log startup information
            logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
            logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
            logger.info(f"Documentation: http://localhost:{settings.PORT}/docs")
            
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise

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

    # OPTIONS route handler for all routes
    @app.options("/{full_path:path}")
    async def options_route(request: Request, full_path: str):
        """Handle OPTIONS requests for all routes."""
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            }
        )

    # Include API routers
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["Authentication"],
        responses={401: {"description": "Unauthorized"}}
    )

    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["Users"],
        responses={401: {"description": "Unauthorized"}}
    )

    app.include_router(
        generator.router,
        prefix="/api/generator",
        tags=["Post Generator"],
        responses={401: {"description": "Unauthorized"}}
    )

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
            if not settings.GROQ_API_KEY:
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
            if not settings.GROQ_API_KEY:
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

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.PROJECT_VERSION,
            "environment": "development" if settings.DEBUG else "production"
        }

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def read_root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "version": settings.PROJECT_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }

    return app

# Create the FastAPI application
app = create_app()

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
