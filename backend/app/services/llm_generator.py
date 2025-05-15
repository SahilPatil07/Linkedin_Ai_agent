import os
import groq
from typing import List, Dict, Tuple, Any, Optional
import logging
from app.core.config import settings
from app.services.linkedin_service import LinkedInService
from dotenv import load_dotenv
import httpx
import json
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self):
        """Initialize the LLM generator with configuration."""
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.linkedin_service = LinkedInService()

    async def generate_chat_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Generate a chat response using the LLM."""
        try:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not set")

            async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
                response = await client.post(
                    f"{settings.GROQ_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": chat_history,
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                        "top_p": settings.TOP_P,
                        "frequency_penalty": settings.FREQUENCY_PENALTY,
                        "presence_penalty": settings.PRESENCE_PENALTY
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise

    def generate_posts(self, topic: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Tuple[List[str], bool]:
        """Generate LinkedIn posts based on the topic and chat history."""
        try:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not set")

            # Prepare the prompt
            prompt = f"""Create {settings.MAX_POSTS_PER_REQUEST} professional LinkedIn posts about {topic}.
            The posts should be engaging, informative, and suitable for a professional audience.
            Format each post with proper spacing and emojis where appropriate.
            Return the posts as a JSON array of strings."""

            # Add chat history context if available
            if chat_history:
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
                prompt = f"{context}\n\n{prompt}"

            # Make the API request
            with httpx.Client(timeout=settings.TIMEOUT) as client:
                response = client.post(
                    f"{settings.GROQ_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                        "top_p": settings.TOP_P,
                        "frequency_penalty": settings.FREQUENCY_PENALTY,
                        "presence_penalty": settings.PRESENCE_PENALTY
                    }
                )
                response.raise_for_status()
                
                # Parse the response
                content = response.json()["choices"][0]["message"]["content"]
                posts = json.loads(content)
                
                # Validate the response
                if not isinstance(posts, list) or len(posts) == 0:
                    raise ValueError("Invalid response format from LLM")
                
                # Limit the number of posts
                posts = posts[:settings.MAX_POSTS_PER_REQUEST]
                
                return posts, True

        except Exception as e:
            logger.error(f"Error generating posts: {str(e)}")
            return [], False

    async def analyze_post_engagement(self, post_id: str) -> Dict:
        """Analyze post engagement metrics."""
        try:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not set")

            prompt = f"""Analyze the engagement metrics for post {post_id}.
            Return the analysis as a JSON object with the following structure:
            {{
                "engagement_score": float,
                "sentiment": str,
                "key_metrics": {{
                    "likes": int,
                    "comments": int,
                    "shares": int
                }},
                "recommendations": List[str]
            }}"""

            async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
                response = await client.post(
                    f"{settings.GROQ_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                        "top_p": settings.TOP_P
                    }
                )
                response.raise_for_status()
                return json.loads(response.json()["choices"][0]["message"]["content"])

        except Exception as e:
            logger.error(f"Error analyzing post engagement: {str(e)}")
            raise

    async def generate_linkedin_post(self, topic: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a LinkedIn post using the LLM."""
        try:
            system_prompt = """You are a professional LinkedIn content creator. 
            Create engaging, professional posts that provide value to the reader.
            Focus on being authentic, informative, and engaging.
            Use appropriate LinkedIn formatting (emojis, line breaks, etc.).
            Keep the tone professional but conversational."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a LinkedIn post about: {topic}"}
            ]
            
            if chat_history:
                messages.extend(chat_history)
            
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                top_p=settings.TOP_P,
                stream=False
            )
            
            return {
                "content": response.choices[0].message.content,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def post_to_linkedin(self, post_content: str) -> Dict:
        """Post content directly to LinkedIn."""
        try:
            result = await self.linkedin_service.create_post(post_content)
            return result
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return {
                "status": "error",
                "message": f"Error posting to LinkedIn: {str(e)}"
            }

    async def schedule_linkedin_post(self, content: str, schedule_time: str) -> Dict[str, Any]:
        """Schedule a LinkedIn post."""
        try:
            # Here you would implement the actual scheduling logic
            # For now, we'll just return a success response
            return {
                "status": "success",
                "message": "Post scheduled successfully",
                "scheduled_time": schedule_time
            }
            
        except Exception as e:
            logger.error(f"Error scheduling post: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 