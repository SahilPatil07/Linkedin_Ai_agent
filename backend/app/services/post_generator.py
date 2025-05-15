import logging
import json
from typing import List, Dict, Any, Tuple, Optional
import httpx
from ..core.config import settings
from ..services.linkedin_service import LinkedInService

logger = logging.getLogger(__name__)

def validate_payload(payload: Dict[str, Any]) -> None:
    """Validate the request payload."""
    required_fields = ["model", "messages"]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(payload["messages"], list):
        raise ValueError("Messages must be a list")
    
    for message in payload["messages"]:
        if not isinstance(message, dict):
            raise ValueError("Each message must be a dictionary")
        if "role" not in message or "content" not in message:
            raise ValueError("Each message must have 'role' and 'content' fields")

async def generate_posts(
    topic: str,
    num_posts: int = 1,
    user_access_token: Optional[str] = None,
    should_post_to_linkedin: bool = True
) -> Tuple[List[str], bool]:
    """
    Generate LinkedIn posts using the Groq API and post to LinkedIn.
    
    Args:
        topic (str): The topic to generate posts about
        num_posts (int): Number of posts to generate (default: 1)
        user_access_token (str): LinkedIn access token for the user
        should_post_to_linkedin (bool): Whether to post directly to LinkedIn
    
    Returns:
        Tuple[List[str], bool]: List of generated post contents and success status
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    if not topic or not isinstance(topic, str):
        raise ValueError("Topic must be a non-empty string")

    if not isinstance(num_posts, int) or num_posts < 1:
        raise ValueError("Number of posts must be a positive integer")

    if not user_access_token:
        raise ValueError("LinkedIn access token is required for posting")

    posts = []
    try:
        # Prepare the request payload
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional LinkedIn content creator. Create engaging, professional posts that provide value to the reader. Each post should be well-structured, include relevant hashtags, and be optimized for LinkedIn's algorithm."
                },
                {
                    "role": "user",
                    "content": f"Generate {num_posts} LinkedIn post{'s' if num_posts > 1 else ''} about {topic}. Each post should be professional, engaging, and provide value to the reader. Format each post with proper spacing and emojis where appropriate. Include relevant hashtags and make it suitable for LinkedIn's professional audience."
                }
            ],
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
            "top_p": settings.TOP_P,
            "frequency_penalty": settings.FREQUENCY_PENALTY,
            "presence_penalty": settings.PRESENCE_PENALTY
        }

        # Validate payload before sending
        validate_payload(payload)

        # Log the request payload (excluding sensitive data)
        safe_payload = payload.copy()
        logger.info("Sending request to Groq API with payload: %s", json.dumps(safe_payload, indent=2))

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Log headers (excluding API key)
        safe_headers = headers.copy()
        safe_headers["Authorization"] = "Bearer [REDACTED]"
        logger.info("Request headers: %s", json.dumps(safe_headers, indent=2))

        # Make the API request
        async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
            response = await client.post(
                f"{settings.GROQ_API_BASE}/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"Groq API error: {response.text}")
                return [], False

            response_data = response.json()
            generated_text = response_data["choices"][0]["message"]["content"]
            
            # Parse the generated text into posts
            try:
                # Try to parse as JSON first
                posts_data = json.loads(generated_text)
                if isinstance(posts_data, dict) and "posts" in posts_data:
                    posts = [post["content"] for post in posts_data["posts"]]
                else:
                    # If not in expected format, split by newlines
                    posts = [p.strip() for p in generated_text.split("\n\n") if p.strip()]
            except json.JSONDecodeError:
                # If not valid JSON, split by newlines
                posts = [p.strip() for p in generated_text.split("\n\n") if p.strip()]

            # Post to LinkedIn
            if posts:
                linkedin_service = LinkedInService()
                
                # Validate the access token
                is_valid = await linkedin_service.validate_token(user_access_token)
                if not is_valid:
                    logger.error("Invalid LinkedIn access token")
                    return posts, False
                
                # Post the first generated post
                result = await linkedin_service.create_post(
                    access_token=user_access_token,
                    content=posts[0],
                    visibility="PUBLIC"
                )
                
                if not result["success"]:
                    logger.error(f"Failed to post to LinkedIn: {result.get('error')}")
                    return posts, False
                
                logger.info("Successfully posted to LinkedIn")
                return posts, True

            return posts, True

    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        return [], False 