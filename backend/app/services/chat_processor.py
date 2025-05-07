import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ChatProcessor:
    """Process LLM responses to extract structured data."""
    
    @staticmethod
    def process_response(response_content: str, user_message: str) -> Tuple[str, bool, Optional[str]]:
        """Process the LLM response to extract structured data.
        
        Args:
            response_content: The raw response from the LLM
            user_message: The original user message
            
        Returns:
            Tuple of (response_text, should_post, post_content)
        """
        # Check if the user's message contains intent to post
        post_intent = ChatProcessor._detect_post_intent(user_message)
        
        # Try to parse JSON from the response
        try:
            data = json.loads(response_content)
            
            # Check if we have a structured posts response
            if "posts" in data and isinstance(data["posts"], list) and len(data["posts"]) > 0:
                # Format the first post for display
                post = data["posts"][0]
                formatted_post = f"{post.get('title', '')}\n\n{post.get('content', '')}"
                
                # Check if should_post flag is set
                should_post = data.get("should_post", False) or post_intent
                
                # Return formatted post as the response
                return formatted_post, should_post, formatted_post
            elif "response" in data:
                # Handle chat response format
                response_text = data["response"]
                should_post = data.get("should_post", False) or post_intent
                post_content = data.get("post_content")
                return response_text, should_post, post_content
            else:
                # Not a properly structured response
                return response_content, post_intent, None
                
        except json.JSONDecodeError:
            # Not a JSON response, treat as plain text
            return response_content, post_intent, None
    
    @staticmethod
    def _detect_post_intent(message: str) -> bool:
        """Detect if the user's message indicates intent to post.
        
        Args:
            message: User's message text
            
        Returns:
            True if posting intent is detected, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Intent phrases that indicate the user wants to post
        intent_phrases = [
            "post it", 
            "yes, post", 
            "please post", 
            "go ahead and post",
            "publish it",
            "share it on linkedin",
            "post to linkedin",
            "share on linkedin",
            "post this",
            "share this"
        ]
        
        # Check if any intent phrase is in the message
        for phrase in intent_phrases:
            if phrase in message_lower:
                return True
                
        return False

    @staticmethod
    def format_post(post: Dict[str, str]) -> str:
        """Format a post for display.
        
        Args:
            post: Dictionary containing post data
            
        Returns:
            Formatted post string
        """
        title = post.get('title', '')
        content = post.get('content', '')
        
        if title:
            return f"{title}\n\n{content}"
        return content

    @staticmethod
    def extract_posts(response_content: str) -> List[Dict[str, str]]:
        """Extract posts from a response.
        
        Args:
            response_content: The response content to parse
            
        Returns:
            List of post dictionaries
        """
        try:
            data = json.loads(response_content)
            if "posts" in data and isinstance(data["posts"], list):
                return data["posts"]
        except json.JSONDecodeError:
            pass
        return [] 