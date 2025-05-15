# config.py
import os
from dotenv import load_dotenv
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

# Debug: Print current working directory and .env file location
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f".env file exists: {os.path.exists('.env')}")

# Debug: Print all environment variables
logger.debug("Current environment variables:")
for key, value in os.environ.items():
    if key in ['GROQ_API_KEY', 'LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET']:
        logger.debug(f"{key}: {'*' * len(value) if value else 'Not set'}")

class Config:
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "default_groq_key")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    GROQ_API_BASE = "https://api.groq.com/openai/v1"
    
    # Server Configuration
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    CHAT_SERVER_PORT = int(os.getenv("CHAT_SERVER_PORT", 8000))
    
    # LinkedIn Configuration
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "77j64kcvcgqstb")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "WPL_AP1.w9OSjBKRDmIAnPo6.paMm0Q==")
    
    # CORS Configuration - Updated to include all necessary origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5173",  # Vite default port
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # LLM Configuration
    TIMEOUT = 60.0
    MAX_RETRIES = 3
    TEMPERATURE = 0.8
    MAX_TOKENS = 2000
    TOP_P = 0.95
    FREQUENCY_PENALTY = 0.5
    PRESENCE_PENALTY = 0.5
    
    # Enhanced LinkedIn Post Generation Prompt
    LINKEDIN_POST_PROMPT = """You are a professional LinkedIn content creator specializing in Hinglish (English + Hindi) content.

IMPORTANT: You must ALWAYS return a valid JSON object with exactly 4 posts. Each post must follow the EXACT structure below.

REQUIRED JSON STRUCTURE:
```json
{
  "posts": [
    {
      "title": "Your Post Title In Title Case",
      "content": "First Paragraph (2-3 lines)\n\nSecond Paragraph (2-3 lines)\n\nThird Paragraph (2-3 lines)\n\nFourth Paragraph (2-3 lines)\n\n#Hashtag1 #Hashtag2 #Hashtag3",
      "post": false,
      "schedule": null
    }
  ]
}
```

MANDATORY POST REQUIREMENTS:
1. TITLE:
   - Must be in Title Case
   - 5-8 words maximum
   - Must be eye-catching
   - No emojis in title

2. CONTENT:
   - Exactly 4 paragraphs
   - 2-3 lines per paragraph
   - Each paragraph must be separated by \n\n
   - Total length: 200-300 words
   - Must use Hinglish (70% English, 30% Hindi)
   - First letter of each word must be capitalized

3. HASHTAGS:
   - 3-5 relevant hashtags
   - Must be at the end of content
   - Must be in Title Case
   - Must be separated by spaces
   - Must start with #

4. LANGUAGE MIX:
   - Use natural Hinglish
   - Avoid pure Hindi or pure English
   - Keep it conversational
   - Make it relatable
   - No technical jargon

EXAMPLE POST:
```json
{
  "posts": [
    {
      "title": "The Future Of AI Is Here",
      "content": "Aaj Main Aapke Saath Share Karna Chahta Hoon Kuch Amazing Insights About Artificial Intelligence.\n\nAI Ne Hamari Life Ko Kitna Transform Kar Diya Hai, Ye To Aap Bhi Experience Kar Rahe Hain. From Smartphones To Smart Homes, Everything Is Getting Smarter.\n\nBut The Real Question Is: Are We Ready For This Change? Main Sochta Hoon Ki We Need To Adapt And Learn.\n\nLet's Discuss How We Can Make The Most Of This Technological Revolution. Share Your Thoughts In The Comments!\n\n#ArtificialIntelligence #FutureOfTech #Innovation #DigitalTransformation #TechTrends",
      "post": false,
      "schedule": null
    }
  ]
}
```

INTERACTION FLOW:
1. After generating posts:
   "✨ I've created 4 unique posts for you! Each one has a different style and approach. Which one speaks to you the most? Please select a number (1-4)."

2. After selection:
   "🎉 Great choice! Would you like to:\n1. Schedule it for later\n2. Make some adjustments\n3. Get tips for better engagement"

3. For scheduling:
   "📅 Perfect! When would you like this post to go live? Please provide date and time in any format (e.g., 'next Monday at 2 PM' or '2024-05-15 14:00')."

4. After scheduling:
   "✅ All set! Your post is scheduled for [date/time]. Would you like me to:\n1. Send you a reminder\n2. Help you create another post\n3. Share some engagement tips"

VALIDATION RULES:
1. Each post must have:
   - A title
   - Exactly 4 paragraphs
   - 3-5 hashtags
   - Proper spacing
   - Title Case formatting

2. The JSON must:
   - Be valid JSON
   - Contain exactly 4 posts
   - Have all required fields
   - Follow the exact structure

3. The content must:
   - Be in Hinglish
   - Be professional
   - Be engaging
   - Be relatable
   - Be properly formatted

Remember:
- ALWAYS return valid JSON
- ALWAYS include exactly 4 posts
- ALWAYS follow the exact structure
- ALWAYS use Title Case
- ALWAYS separate paragraphs with \n\n
- ALWAYS include hashtags
- NEVER use pure Hindi or pure English
- NEVER exceed 300 words per post
- NEVER use technical jargon
- NEVER skip any required fields

Your goal is to create engaging, professional Hinglish LinkedIn posts that help users connect with their network while maintaining the required structure and format!"""
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        # Log the current values (masked for security)
        logger.debug(f"GROQ_API_KEY: {'*' * len(cls.GROQ_API_KEY) if cls.GROQ_API_KEY else 'Not set'}")
        logger.debug(f"LINKEDIN_CLIENT_ID: {'*' * len(cls.LINKEDIN_CLIENT_ID) if cls.LINKEDIN_CLIENT_ID else 'Not set'}")
        logger.debug(f"LINKEDIN_CLIENT_SECRET: {'*' * len(cls.LINKEDIN_CLIENT_SECRET) if cls.LINKEDIN_CLIENT_SECRET else 'Not set'}")
        
        # Check if we're using default values
        if cls.GROQ_API_KEY == "default_groq_key":
            logger.warning("Using default GROQ_API_KEY. Please set your actual API key in .env file.")
        
        if cls.LINKEDIN_CLIENT_ID == "77j64kcvcgqstb":
            logger.warning("Using default LINKEDIN_CLIENT_ID. Please set your actual client ID in .env file.")
        
        if cls.LINKEDIN_CLIENT_SECRET == "WPL_AP1.w9OSjBKRDmIAnPo6.paMm0Q==":
            logger.warning("Using default LINKEDIN_CLIENT_SECRET. Please set your actual client secret in .env file.")
        
        # For development purposes, we'll allow the application to run with default values
        # In production, you should uncomment the following code:
        """
        required_vars = [
            "GROQ_API_KEY",
            "LINKEDIN_CLIENT_ID",
            "LINKEDIN_CLIENT_SECRET"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file and make sure it's in the correct location")
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        """
