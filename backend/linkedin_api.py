import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def post_to_linkedin(text, media_url=None):
    """
    Post content to LinkedIn using the API
    """
    # Get access token from environment variables
    linkedin_access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')
    
    if not linkedin_access_token:
        raise ValueError("LinkedIn access token not found. Make sure LINKEDIN_ACCESS_TOKEN is set in your .env file.")
    
    headers = {
        'Authorization': f'Bearer {linkedin_access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        # Get user's URN
        profile_url = 'https://api.linkedin.com/v2/me'
        profile_response = requests.get(profile_url, headers=headers)
        if profile_response.status_code != 200:
            logger.error(f"Failed to get profile: {profile_response.text}")
            return profile_response.status_code, profile_response.json()
        
        author_urn = profile_response.json()['id']
        
        # Prepare post data
        post_data = {
            "author": f"urn:li:person:{author_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add media if provided
        if media_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "description": {
                    "text": text
                },
                "originalUrl": media_url,
                "title": {
                    "text": "LinkedIn Post"
                }
            }]
        
        # Post to LinkedIn
        post_url = 'https://api.linkedin.com/v2/ugcPosts'
        response = requests.post(post_url, headers=headers, json=post_data)
        
        if response.status_code not in (200, 201):
            logger.error(f"Failed to create post: {response.text}")
            return response.status_code, response.json()
        
        logger.info("Successfully created LinkedIn post")
        return response.status_code, response.json()
        
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        return 500, {"error": str(e)}