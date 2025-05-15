from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from app.services.linkedin_service import LinkedInService
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
linkedin_service = LinkedInService()

@router.get("/verify")
async def verify_linkedin_connection() -> Dict[str, Any]:
    """Verify LinkedIn connection and token validity."""
    try:
        logger.info("Verifying LinkedIn connection...")
        result = await linkedin_service.verify_token()
        
        if result["status"] == "error":
            logger.error(f"LinkedIn verification failed: {result['message']}")
            return {
                "status": "error",
                "message": result["message"],
                "needs_config": "LINKEDIN_ACCESS_TOKEN" in result["message"]
            }
            
        logger.info("LinkedIn connection verified successfully")
        return {
            "status": "success",
            "message": "LinkedIn connection verified",
            "profile": result.get("profile")
        }
        
    except Exception as e:
        error_msg = f"Error verifying LinkedIn connection: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@router.post("/posts")
async def create_linkedin_post(content: str) -> Dict[str, Any]:
    """Create a new LinkedIn post."""
    try:
        logger.info("Creating LinkedIn post...")
        result = await linkedin_service.create_post(content)
        
        if not result["success"]:
            if result.get("needs_auth"):
                logger.error("LinkedIn authentication required")
                return {
                    "status": "error",
                    "message": "LinkedIn authentication required",
                    "needs_auth": True
                }
            logger.error(f"Failed to create post: {result['error']}")
            return {
                "status": "error",
                "message": result["error"]
            }
            
        logger.info("LinkedIn post created successfully")
        return result
        
    except Exception as e:
        error_msg = f"Error creating LinkedIn post: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@router.get("/permissions")
async def check_linkedin_permissions() -> Dict[str, Any]:
    """Check LinkedIn token permissions."""
    try:
        logger.info("Checking LinkedIn permissions...")
        result = await linkedin_service.verify_token_permissions()
        logger.info("LinkedIn permissions checked successfully")
        return result
        
    except Exception as e:
        error_msg = f"Error checking LinkedIn permissions: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@router.get("/test")
async def test_linkedin_service() -> Dict[str, Any]:
    """Test endpoint to verify LinkedIn service is working."""
    try:
        logger.info("Testing LinkedIn service...")
        return {
            "status": "success",
            "message": "LinkedIn service is working",
            "service_info": {
                "api_base_url": linkedin_service.api_base_url,
                "has_access_token": bool(linkedin_service.access_token),
                "has_refresh_token": bool(linkedin_service.refresh_token),
                "user_id": linkedin_service.user_id
            }
        }
    except Exception as e:
        logger.error(f"Error testing LinkedIn service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-token")
async def refresh_linkedin_token() -> Dict[str, Any]:
    """Refresh the LinkedIn access token."""
    try:
        logger.info("Attempting to refresh LinkedIn token...")
        success = await linkedin_service.refresh_access_token()
        
        if success:
            logger.info("Successfully refreshed LinkedIn token")
            return {
                "status": "success",
                "message": "Token refreshed successfully"
            }
        else:
            logger.error("Failed to refresh LinkedIn token")
            return {
                "status": "error",
                "message": "Failed to refresh token. Please re-authenticate.",
                "needs_auth": True
            }
            
    except Exception as e:
        error_msg = f"Error refreshing token: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@router.get("/token-status")
async def check_token_status() -> Dict[str, Any]:
    """Check the current status of the LinkedIn token."""
    try:
        logger.info("Checking LinkedIn token status...")
        return {
            "status": "success",
            "token_info": {
                "has_access_token": bool(linkedin_service.access_token),
                "has_refresh_token": bool(linkedin_service.refresh_token),
                "user_id": linkedin_service.user_id,
                "api_base_url": linkedin_service.api_base_url
            }
        }
    except Exception as e:
        error_msg = f"Error checking token status: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

@router.get("/auth-url")
async def get_linkedin_auth_url() -> Dict[str, Any]:
    """Get the LinkedIn OAuth URL for authentication."""
    try:
        auth_url = (
            f"{settings.LINKEDIN_AUTH_URL}"
            f"?response_type=code"
            f"&client_id={settings.LINKEDIN_CLIENT_ID}"
            f"&redirect_uri={settings.LINKEDIN_REDIRECT_URI}"
            f"&scope={settings.LINKEDIN_SCOPE}"
        )
        return {
            "status": "success",
            "auth_url": auth_url
        }
    except Exception as e:
        error_msg = f"Error generating auth URL: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        } 