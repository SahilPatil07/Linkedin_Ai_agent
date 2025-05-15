import httpx
import logging
from typing import Dict, List, Optional, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.timeout = settings.TIMEOUT
        self.api_url = settings.GROQ_API_BASE

    async def get_chat_response(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Get a response from the chat model.
        
        Args:
            message: The user's message
            chat_history: Previous chat messages for context
            
        Returns:
            Dict containing the response and any additional data
        """
        try:
            # If the message indicates a post request
            if any(keyword in message.lower() for keyword in ["post", "share", "publish", "create post"]):
                # Generate a post
                post_content = await self.generate_post(message)
                return {
                    "status": "success",
                    "message": f"Post content:\n{post_content}",
                    "is_post": True
                }
            
            # Otherwise, generate a normal response
            response = await self.generate_response(message, chat_history)
            return {
                "status": "success",
                "message": response,
                "is_post": False
            }
            
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def generate_post(self, prompt: str) -> str:
        """
        Generate a LinkedIn post based on the prompt.
        
        Args:
            prompt: The user's prompt for the post
            
        Returns:
            The generated post content
        """
        try:
            # Prepare the system message
            system_message = """You are a professional LinkedIn content creator. 
            Generate engaging, professional posts that are:
            1. Clear and concise
            2. Professional in tone
            3. Include relevant hashtags
            4. End with a call to action
            5. Optimized for LinkedIn's algorithm
            
            Format the post with:
            - A compelling headline
            - 2-3 paragraphs of content
            - 3-5 relevant hashtags
            - A call to action
            
            Keep the total length under 1300 characters."""
            
            # Generate the post
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                        "top_p": settings.TOP_P,
                        "frequency_penalty": settings.FREQUENCY_PENALTY,
                        "presence_penalty": settings.PRESENCE_PENALTY
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not content:
                        raise Exception("Empty response from Groq API")
                    return content
                else:
                    error_msg = f"Failed to generate post: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Error generating post: {str(e)}")
            raise Exception(f"Failed to generate post: {str(e)}")

    async def generate_response(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a response from the chat model
        """
        if not self.api_key:
            return "GROQ API key is not configured"

        try:
            # Prepare messages
            messages = []
            if chat_history:
                messages.extend(chat_history)
            messages.append({"role": "user", "content": message})

            # Generate response
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": settings.TEMPERATURE,
                        "max_tokens": settings.MAX_TOKENS,
                        "top_p": settings.TOP_P,
                        "frequency_penalty": settings.FREQUENCY_PENALTY,
                        "presence_penalty": settings.PRESENCE_PENALTY
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not content:
                        raise Exception("Empty response from Groq API")
                    return content
                else:
                    error_msg = f"Chat API error: {response.text}"
                    logger.error(error_msg)
                    return error_msg

        except Exception as e:
            error_msg = f"Error getting chat response: {str(e)}"
            logger.error(error_msg)
            return error_msg 