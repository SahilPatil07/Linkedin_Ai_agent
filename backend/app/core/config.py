from pydantic_settings import BaseSettings
from typing import List, Optional, Tuple, Dict, Union
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
import httpx
from pydantic import AnyHttpUrl, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "LinkedIn Post Generator"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # LinkedIn API
    LINKEDIN_API_URL: str = "https://api.linkedin.com/v2"
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "")
    LINKEDIN_USER_ID: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_REFRESH_TOKEN: str = os.getenv("LINKEDIN_REFRESH_TOKEN", "")
    LINKEDIN_AUTH_URL: str = "https://www.linkedin.com/oauth/v2/authorization"
    LINKEDIN_TOKEN_URL: str = "https://www.linkedin.com/oauth/v2/accessToken"
    LINKEDIN_SCOPE: str = os.getenv("LINKEDIN_SCOPE", "w_member_social,r_organization_social")
    LINKEDIN_ORGANIZATION_ID: str = os.getenv("LINKEDIN_ORGANIZATION_ID", "")

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    TOP_P: float = 1.0
    FREQUENCY_PENALTY: float = 0.0
    PRESENCE_PENALTY: float = 0.0

    # Timeout
    TIMEOUT: int = 30

    # Post Generation
    MAX_POSTS_PER_REQUEST: int = 5
    MAX_SCHEDULED_POSTS: int = 10
    POST_GENERATION_TIMEOUT: int = 30

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env file

settings = Settings()

# Log current configuration (excluding sensitive data)
logger.debug(f"Current working directory: {Path.cwd()}")
logger.debug(f".env file exists: {Path('.env').exists()}")
logger.debug("Current environment variables:")
logger.debug(f"GROQ_API_KEY: {'*' * 20 if settings.GROQ_API_KEY else 'Not set'}")
logger.debug(f"LINKEDIN_ACCESS_TOKEN: {'*' * 20 if settings.LINKEDIN_ACCESS_TOKEN else 'Not set'}")

async def generate_posts(self, topic: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Tuple[List[str], bool]:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    posts = []
    for _ in range(settings.MAX_POSTS_PER_REQUEST):
        async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
            response = await client.post(
                f"{settings.GROQ_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "temperature": settings.TEMPERATURE,
                    # ... other settings
                }
            )
            if response.status_code == 200:
                posts.append(response.json().get("choices", [{}])[0].get("message", {}).get("content", ""))
            else:
                logger.error(f"API call failed with status code: {response.status_code}")
                return posts, False

    posts = posts[:settings.MAX_POSTS_PER_REQUEST]
    return posts, True 

def __init__(self):
    self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
    self.linkedin_service = LinkedInService()