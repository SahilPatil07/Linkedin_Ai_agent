import httpx
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator, Optional, Union, Tuple
from app.core.config import config

logger = logging.getLogger(__name__)

class LLMGenerator:
    """Class for handling LLM-based LinkedIn post generation using Groq."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """Initialize with optional overrides for configuration values."""
        self.api_key = api_key or config.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not set. API calls will fail.")
            
        self.model = model or config.GROQ_MODEL
        self.api_base = api_base or config.GROQ_API_BASE
        self.timeout = timeout or config.TIMEOUT
        self.max_retries = max_retries or config.MAX_RETRIES
        
    def _validate_api_key(self):
        """Validate that the API key is set."""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured")
            
    def _construct_prompt(self, topic: str) -> str:
        """Construct a prompt for the LLM to generate LinkedIn posts."""
        return config.LINKEDIN_POST_PROMPT.format(topic=topic)
    
    def _construct_system_message(self) -> Dict[str, str]:
        """Construct a system message for the LLM."""
        return {
            "role": "system",
            "content": "You are a professional LinkedIn content creator specializing in Hinglish content. Your task is to create engaging, professional posts according to the user's requirements."
        }
    
    async def generate_posts_async(
        self, 
        topic: str, 
        chat_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Generate LinkedIn posts asynchronously."""
        try:
            self._validate_api_key()
            
            messages = []
            
            # Add system message
            messages.append(self._construct_system_message())
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history)
            
            # Add user message with topic
            messages.append({
                "role": "user",
                "content": self._construct_prompt(topic)
            })
            
            # If streaming is requested, use the streaming endpoint
            if stream:
                return self._generate_streaming(messages)
            
            # Otherwise use regular completion
            retry_count = 0
            while retry_count < self.max_retries:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }
                        
                        payload = {
                            "model": self.model,
                            "messages": messages,
                            "temperature": config.TEMPERATURE,
                            "max_tokens": config.MAX_TOKENS,
                            "top_p": config.TOP_P,
                            "frequency_penalty": config.FREQUENCY_PENALTY,
                            "presence_penalty": config.PRESENCE_PENALTY
                        }
                        
                        logger.debug(f"Making request to {self.api_base}/chat/completions")
                        logger.debug(f"Headers: {headers}")
                        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                        
                        response = await client.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        
                        response.raise_for_status()
                        return response.json()
                        
                except httpx.TimeoutException as e:
                    logger.error(f"Timeout error (try {retry_count + 1}/{self.max_retries}): {str(e)}")
                    retry_count += 1
                    await asyncio.sleep(1)
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error (try {retry_count + 1}/{self.max_retries}): {str(e)}")
                    logger.error(f"Response content: {e.response.content}")
                    retry_count += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Unexpected error (try {retry_count + 1}/{self.max_retries}): {str(e)}")
                    retry_count += 1
                    await asyncio.sleep(1)
            
            raise Exception("Failed to generate posts after multiple retries")
            
        except Exception as e:
            logger.error(f"Error in generate_posts_async: {str(e)}")
            raise
    
    async def generate_chat_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Generate a chat response based on the conversation history."""
        try:
            self._validate_api_key()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Ensure chat history has valid roles
                validated_messages = []
                for msg in chat_history:
                    role = msg.get("role", "").lower()
                    if role not in ["system", "user", "assistant"]:
                        role = "user"  # Default to user if role is invalid
                    validated_messages.append({
                        "role": role,
                        "content": msg.get("content", "")
                    })
                
                payload = {
                    "model": self.model,
                    "messages": validated_messages,
                    "temperature": config.TEMPERATURE,
                    "max_tokens": config.MAX_TOKENS,
                    "top_p": config.TOP_P,
                    "frequency_penalty": config.FREQUENCY_PENALTY,
                    "presence_penalty": config.PRESENCE_PENALTY
                }
                
                logger.debug(f"Making request to {self.api_base}/chat/completions")
                logger.debug(f"Headers: {headers}")
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response text
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to Groq API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
            raise Exception(f"Groq API returned an error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise Exception(f"Failed to generate chat response: {str(e)}")
    
    def generate_posts(self, topic: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Tuple[List[str], bool]:
        """Generate LinkedIn posts synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result = loop.run_until_complete(self.generate_posts_async(topic, chat_history))
        
        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            try:
                data = json.loads(content)
                if not isinstance(data, dict):
                    logger.warning(f"Expected dict from JSON parse, got {type(data)}")
                    data = {"posts": [], "should_post": False}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                data = {"posts": [], "should_post": False}
            
            posts = []
            should_post = False
            
            if "posts" in data and isinstance(data["posts"], list):
                posts = [f"{post.get('title', '')}\n\n{post.get('content', '')}" for post in data["posts"]]
                should_post = data.get("should_post", False)
            else:
                logger.warning("Unexpected response format. Missing 'posts' array.")
                posts = [content]
                
            return posts, should_post
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            
            if "choices" in result and len(result["choices"]) > 0:
                return [result["choices"][0]["message"]["content"]], False
            else:
                return ["Error generating posts. Please try again."], False

    async def _generate_streaming(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate response in streaming mode."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": config.TEMPERATURE,
                        "max_tokens": config.MAX_TOKENS,
                        "stream": True  # Enable streaming
                    },
                    stream=True
                )
                
                response.raise_for_status()
                
                # Process the streaming response
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        try:
                            chunk_data = json.loads(line[6:])  # Remove "data: " prefix
                            content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield {
                                    "content": content,
                                    "model": self.model,
                                    "timestamp": datetime.now().isoformat()
                                }
                        except json.JSONDecodeError:
                            pass
                    elif line.startswith("data: [DONE]"):
                        break
                        
        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            yield {"error": str(e)} 