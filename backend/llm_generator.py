# llm_generator.py
import asyncio
import os
from dotenv import load_dotenv
from fastapi import WebSocket
from config import Config
from typing import List, Dict, Optional, AsyncGenerator, Any, Union
import json
import httpx
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class PostValidationError(Exception):
    """Custom exception for post validation errors."""
    pass

class LLMGenerator:
    """Class for handling LLM-based LinkedIn post generation."""
    
    def __init__(self):
        try:
            self.api_key = Config.GROQ_API_KEY
            self.model = Config.GROQ_MODEL
            self.api_base = Config.GROQ_API_BASE
            self.timeout = Config.TIMEOUT
            self.max_retries = Config.MAX_RETRIES
            self.conversation_history = []
            logger.info(f"Initialized LLMGenerator with model: {self.model}")
        except Exception as e:
            logger.error(f"Error initializing LLMGenerator: {str(e)}")
            raise
            
    def _construct_prompt(self, topic: str) -> str:
        """Construct a prompt for the LLM to generate LinkedIn posts."""
        return Config.LINKEDIN_POST_PROMPT + f"\n\nTopic: {topic}"
    
    def _construct_system_message(self) -> Dict[str, str]:
        """Construct a system message for the LLM."""
        return {
            "role": "system",
            "content": "You are a professional LinkedIn content creator specializing in Hinglish content. Your task is to create engaging, professional posts according to the user's requirements."
        }
    
    def _validate_post(self, post: Dict[str, Any]) -> bool:
        """Validate a single post against required format."""
        try:
            # Check required fields
            if not all(key in post for key in ['title', 'content', 'post', 'schedule']):
                raise PostValidationError("Missing required fields in post")
            
            # Validate title
            if not isinstance(post['title'], str) or len(post['title'].split()) > 8:
                raise PostValidationError("Invalid title format or length")
            
            # Validate content
            content = post['content']
            paragraphs = content.split('\n\n')
            if len(paragraphs) < 4:  # 4 paragraphs + hashtags
                raise PostValidationError("Insufficient paragraphs in content")
            
            # Validate hashtags
            hashtags = [tag for tag in content.split() if tag.startswith('#')]
            if not (3 <= len(hashtags) <= 5):
                raise PostValidationError("Invalid number of hashtags")
            
            # Validate boolean fields
            if not isinstance(post['post'], bool):
                raise PostValidationError("Invalid post field type")
            if post['schedule'] is not None and not isinstance(post['schedule'], str):
                raise PostValidationError("Invalid schedule field type")
            
            return True
            
        except Exception as e:
            logger.error(f"Post validation error: {str(e)}")
            return False
    
    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate the complete LLM response."""
        try:
            if not isinstance(data, dict):
                raise PostValidationError("Response is not a dictionary")
            
            if 'posts' not in data:
                raise PostValidationError("Missing 'posts' array in response")
            
            if not isinstance(data['posts'], list) or len(data['posts']) != 4:
                raise PostValidationError("Invalid number of posts")
            
            # Validate each post
            for post in data['posts']:
                if not self._validate_post(post):
                    raise PostValidationError("Invalid post format")
            
            return True
            
        except Exception as e:
            logger.error(f"Response validation error: {str(e)}")
            return False
    
    async def generate_posts_async(self, topic: str, chat_history: Optional[List[dict]] = None) -> Dict[str, Any]:
        """Generate LinkedIn posts asynchronously."""
        messages = []
        
        # Add system message
        messages.append(self._construct_system_message())
        
        # Add chat history if provided
        if chat_history:
            for message in chat_history:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        # Add user message with topic
        messages.append({
            "role": "user",
            "content": self._construct_prompt(topic)
        })
        
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.api_base}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": Config.TEMPERATURE,
                            "max_tokens": Config.MAX_TOKENS,
                            "top_p": Config.TOP_P,
                            "frequency_penalty": Config.FREQUENCY_PENALTY,
                            "presence_penalty": Config.PRESENCE_PENALTY,
                            "response_format": {"type": "json_object"}
                        }
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract and validate content
                    content = result["choices"][0]["message"]["content"]
                    data = json.loads(content)
                    
                    if self._validate_response(data):
                        return result
                    else:
                        raise PostValidationError("Response validation failed")
                    
            except Exception as e:
                last_error = e
                logger.error(f"Error generating posts (try {retry_count + 1}/{self.max_retries}): {str(e)}")
                retry_count += 1
                await asyncio.sleep(1)  # Wait before retrying
        
        # If we've exhausted retries, raise the last error
        raise Exception(f"Failed to generate posts after {self.max_retries} retries. Last error: {str(last_error)}")
    
    def generate_posts(self, topic: str, chat_history: Optional[List[dict]] = None) -> List[Dict[str, Any]]:
        """Generate LinkedIn posts synchronously."""
        try:
            result = asyncio.run(self.generate_posts_async(topic, chat_history))
            content = result["choices"][0]["message"]["content"]
            data = json.loads(content)
            
            if self._validate_response(data):
                return data["posts"]
            else:
                raise PostValidationError("Response validation failed")
                
        except Exception as e:
            logger.error(f"Error in generate_posts: {str(e)}")
            return [{
                "title": "Error Generating Posts",
                "content": "We encountered an error while generating your posts. Please try again.",
                "post": False,
                "schedule": None
            }]

async def generate_posts_stream(topic: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream generate LinkedIn posts for a topic."""
    generator = LLMGenerator()
    
    try:
        result = await generator.generate_posts_async(topic)
        content = result["choices"][0]["message"]["content"]
        data = json.loads(content)
        
        if not generator._validate_response(data):
            raise PostValidationError("Response validation failed")
        
        # Stream each post separately
        for post in data["posts"]:
            # Stream title
            yield {
                "type": "title",
                "content": post["title"],
                "model": generator.model,
                "timestamp": datetime.now().isoformat()
            }
            await asyncio.sleep(0.2)
            
            # Stream content paragraphs
            paragraphs = post["content"].split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    yield {
                        "type": "paragraph",
                        "content": paragraph,
                        "model": generator.model,
                        "timestamp": datetime.now().isoformat()
                    }
                    await asyncio.sleep(0.1)
            
            # Stream hashtags
            hashtags = [tag for tag in post["content"].split() if tag.startswith('#')]
            if hashtags:
                yield {
                    "type": "hashtags",
                    "content": ' '.join(hashtags),
                    "model": generator.model,
                    "timestamp": datetime.now().isoformat()
                }
            
            await asyncio.sleep(0.3)  # Pause between posts
            
    except Exception as e:
        logger.error(f"Error in streaming generation: {str(e)}")
        yield {
            "type": "error",
            "content": str(e),
            "model": generator.model,
            "timestamp": datetime.now().isoformat()
        }
