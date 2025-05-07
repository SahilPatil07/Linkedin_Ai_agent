import os
from pathlib import Path
from typing import List, Optional, Annotated
from pydantic_settings import BaseSettings
from pydantic import validator, StringConstraints
import logging
import re

logger = logging.getLogger(__name__)

class Config(BaseSettings):
    """Application configuration."""
    
    # API Keys
    GROQ_API_KEY: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    
    # Application Settings
    DEBUG: bool = False
    APP_NAME: str = "LinkedIn Post Generator"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]  # Frontend URL
    
    # LinkedIn Settings
    LINKEDIN_ORGANIZATION_URN: Annotated[str, StringConstraints(pattern=r'^urn:li:organization:\d+$')] = "urn:li:organization:107281847"
    
    @validator('LINKEDIN_ORGANIZATION_URN')
    def validate_organization_urn(cls, v):
        """Validate the LinkedIn organization URN format."""
        if not re.match(r'^urn:li:organization:\d+$', v):
            raise ValueError('Invalid LinkedIn organization URN format. Must be in format: urn:li:organization:ID')
        return v
    
    # Groq API Settings
    GROQ_MODEL: str = "llama3-70b-8192"  # Using Mixtral model
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"  # Correct Groq API endpoint
    
    # API Settings
    TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    TOP_P: float = 0.95
    FREQUENCY_PENALTY: float = 0.0
    PRESENCE_PENALTY: float = 0.0
    
    # LinkedIn Post Generation
    LINKEDIN_POST_PROMPT: str = """
    Create a professional LinkedIn post about {topic}. The post should be engaging and informative.
    Format the response as a JSON object with the following structure:
    {{
        "posts": [
            {{
                "title": "Post Title",
                "content": "Post content in Hinglish"
            }}
        ],
        "should_post": true/false
    }}
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in .env file
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configure logging based on DEBUG setting
        logging.basicConfig(
            level=logging.DEBUG if self.DEBUG else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Log configuration state (excluding sensitive data)
        logger.info("Configuration loaded:")
        logger.info(f"DEBUG: {self.DEBUG}")
        logger.info(f"APP_NAME: {self.APP_NAME}")
        logger.info(f"GROQ_MODEL: {self.GROQ_MODEL}")
        logger.info(f"GROQ_API_BASE: {self.GROQ_API_BASE}")
        logger.info(f"TIMEOUT: {self.TIMEOUT}")
        logger.info(f"MAX_RETRIES: {self.MAX_RETRIES}")
        
        # Log warnings for missing API keys
        if not self.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set")
        if not self.LINKEDIN_ACCESS_TOKEN:
            logger.warning("LINKEDIN_ACCESS_TOKEN is not set")

# Create global config instance
config = Config()

# Log current configuration (excluding sensitive data)
logger.debug(f"Current working directory: {Path.cwd()}")
logger.debug(f".env file exists: {Path('.env').exists()}")
logger.debug("Current environment variables:")
logger.debug(f"GROQ_API_KEY: {'*' * 20 if config.GROQ_API_KEY else 'Not set'}")
logger.debug(f"LINKEDIN_ACCESS_TOKEN: {'*' * 20 if config.LINKEDIN_ACCESS_TOKEN else 'Not set'}") 