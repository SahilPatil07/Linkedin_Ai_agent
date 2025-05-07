from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
import os
import logging
from dotenv import load_dotenv
from typing import Optional, List
import time
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Post Generator API",
    description="API for generating LinkedIn posts using Llama-3.3-70B-Versatile",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=10, max_length=1000)
    temperature: Optional[float] = Field(default=Config.TEMPERATURE, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=Config.MAX_TOKENS, ge=100, le=4000)
    top_p: Optional[float] = Field(default=Config.TOP_P, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=Config.FREQUENCY_PENALTY, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=Config.PRESENCE_PENALTY, ge=-2.0, le=2.0)

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: float = Field(default_factory=time.time)

class PostResponse(BaseModel):
    posts: List[str]
    metadata: dict

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )

@app.post("/chat", response_model=PostResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    if not Config.GROQ_API_KEY:
        logger.error("GROQ_API_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="API key not configured"
        )

    logger.info(f"Processing chat request: {request.message[:50]}...")
    
    for attempt in range(Config.MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
                response = await client.post(
                    f"{Config.GROQ_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.GROQ_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": Config.LINKEDIN_POST_PROMPT
                            },
                            {
                                "role": "user",
                                "content": request.message
                            }
                        ],
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                        "top_p": request.top_p,
                        "frequency_penalty": request.frequency_penalty,
                        "presence_penalty": request.presence_penalty
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Process and validate the response
                    posts = [post.strip() for post in content.split('\n\n') if post.strip()]
                    if len(posts) != 3:
                        logger.warning(f"Expected 3 posts, got {len(posts)}")
                    
                    logger.info("Successfully generated LinkedIn posts")
                    return PostResponse(
                        posts=posts,
                        metadata={
                            "model": Config.GROQ_MODEL,
                            "tokens_used": data["usage"]["total_tokens"],
                            "timestamp": time.time()
                        }
                    )
                    
                elif response.status_code == 429:  # Rate limit
                    if attempt < Config.MAX_RETRIES - 1:
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                else:
                    logger.error(f"Groq API error: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error from Groq API: {response.text}"
                    )
                
        except httpx.TimeoutException:
            if attempt < Config.MAX_RETRIES - 1:
                logger.warning(f"Timeout occurred. Retrying... (Attempt {attempt + 1}/{Config.MAX_RETRIES})")
                continue
            raise HTTPException(status_code=504, detail="Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    raise HTTPException(status_code=500, detail="Max retries exceeded")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model": Config.GROQ_MODEL,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting chat server on port {Config.CHAT_SERVER_PORT}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Config.CHAT_SERVER_PORT,
        log_level="info"
    ) 