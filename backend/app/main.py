from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import time
import signal
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import chat_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Chat API",
    description="API for AI-powered chat interactions",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include chat router with both paths to ensure compatibility
app.include_router(
    chat_router,
    prefix=f"{settings.API_V1_STR}",
    tags=["chat"]
)

# Add a second route for /chat to handle direct requests
app.include_router(
    chat_router,
    prefix="",
    tags=["chat"]
)

# Log all registered routes on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    logger.info("Registered routes:")
    for route in app.routes:
        logger.info(f"Route: {route.path} [{route.methods}]")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    yield
    # Shutdown
    logger.info("Shutting down application...")

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Method: {request.method} Path: {request.url.path} Status: {response.status_code} Duration: {process_time:.2f}s")
    return response

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Chat API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Signal handlers for graceful shutdown
def handle_sigterm(*args):
    logger.info("Received SIGTERM signal. Starting graceful shutdown...")
    raise KeyboardInterrupt()

def handle_sigint(*args):
    logger.info("Received SIGINT signal. Starting graceful shutdown...")
    raise KeyboardInterrupt()

# Register signal handlers
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigint)