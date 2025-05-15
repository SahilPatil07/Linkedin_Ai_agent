import os
import logging
import json
from typing import Dict, Any, Optional
import requests
from datetime import datetime
from dotenv import load_dotenv
import httpx
from ..core.config import settings

load_dotenv()

logger = logging.getLogger(__name__)

class LinkedInService:
    """Service for interacting with LinkedIn API."""
    
    def __init__(self):
        try:
            self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
            self.refresh_token = os.getenv("LINKEDIN_REFRESH_TOKEN")
            self.api_base_url = settings.LINKEDIN_API_URL
            self.timeout = settings.TIMEOUT
            self.headers = {
                "Authorization": f"Bearer {self.access_token}" if self.access_token else "",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            self.user_id = settings.LINKEDIN_USER_ID
            
            # Log initialization
            logger.info("LinkedInService initialized")
            logger.debug(f"API Base URL: {self.api_base_url}")
            logger.debug(f"Access Token: {'*' * 10 if self.access_token else 'Not set'}")
            logger.debug(f"User ID: {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error initializing LinkedInService: {str(e)}")
            raise

    def _update_headers(self):
        """Update headers with current access token"""
        self.headers["Authorization"] = f"Bearer {self.access_token}" if self.access_token else ""

    async def verify_authentication(self) -> bool:
        """
        Verify if the current authentication is valid
        """
        try:
            if not self.access_token:
                logger.info("No access token available")
                return False

            self._update_headers()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base_url}/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    profile_data = response.json()
                    self.user_id = profile_data.get("id")
                    os.environ["LINKEDIN_USER_ID"] = self.user_id
                    logger.info(f"Successfully verified authentication for user: {self.user_id}")
                    return True
                else:
                    logger.error(f"Authentication verification failed: {response.text}")
                    # Clear invalid tokens
                    self.access_token = None
                    self.refresh_token = None
                    os.environ.pop("LINKEDIN_ACCESS_TOKEN", None)
                    os.environ.pop("LINKEDIN_REFRESH_TOKEN", None)
                    os.environ.pop("LINKEDIN_USER_ID", None)
                    return False

        except Exception as e:
            logger.error(f"Error verifying authentication: {str(e)}")
            return False

    async def refresh_access_token(self) -> bool:
        """
        Refresh the LinkedIn access token using the refresh token
        """
        try:
            if not self.refresh_token:
                logger.error("No refresh token available")
                return False

            logger.info("Attempting to refresh access token")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token,
                        "client_id": settings.LINKEDIN_CLIENT_ID,
                        "client_secret": settings.LINKEDIN_CLIENT_SECRET
                    }
                )

                if response.status_code == 200:
                    token_data = response.json()
                    logger.info("Successfully received new access token")
                    
                    # Update access token
                    self.access_token = token_data["access_token"]
                    self._update_headers()
                    
                    # Update environment variable
                    os.environ["LINKEDIN_ACCESS_TOKEN"] = self.access_token
                    
                    # If a new refresh token is provided, update it
                    if "refresh_token" in token_data:
                        logger.info("Received new refresh token")
                        self.refresh_token = token_data["refresh_token"]
                        os.environ["LINKEDIN_REFRESH_TOKEN"] = self.refresh_token
                    
                    # Verify the new token works
                    verify_result = await self.verify_token()
                    if verify_result["status"] == "success":
                        logger.info("Successfully verified new token")
                        return True
                    else:
                        logger.error(f"New token verification failed: {verify_result['message']}")
                        return False
                else:
                    error_msg = f"Failed to refresh token: {response.text}"
                    logger.error(error_msg)
                    # Clear invalid tokens
                    self.access_token = None
                    self.refresh_token = None
                    os.environ.pop("LINKEDIN_ACCESS_TOKEN", None)
                    os.environ.pop("LINKEDIN_REFRESH_TOKEN", None)
                    os.environ.pop("LINKEDIN_USER_ID", None)
                    return False

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False

    async def create_post(
        self,
        content: str,
        visibility: str = "PUBLIC",
        media_category: str = "NONE",
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a post on LinkedIn company page.
        
        Args:
            content: Post content text
            visibility: Post visibility (PUBLIC, CONNECTIONS)
            media_category: Type of media (NONE, ARTICLE, IMAGE, VIDEO)
            media_url: URL of the media if any
            
        Returns:
            Dict containing the response from LinkedIn API
        """
        try:
            # First verify authentication
            if not self.access_token:
                logger.error("No access token available")
                return {
                    "success": False,
                    "error": "LinkedIn access token not configured",
                    "needs_auth": True
                }

            # Get organization URN
            org_urn = f"urn:li:organization:{settings.LINKEDIN_ORGANIZATION_ID}"
            logger.info(f"Using organization URN: {org_urn}")
            
            # Prepare post data
            post_data = {
                "author": org_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": media_category
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Add media if provided
            if media_url and media_category != "NONE":
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": "Media description"
                    },
                    "originalUrl": media_url,
                    "title": {
                        "text": "LinkedIn Post"
                    }
                }]
            
            # Try to create post
            logger.info("Attempting to create LinkedIn post...")
            logger.debug(f"Post data: {json.dumps(post_data, indent=2)}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base_url}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                )
            
            # If token is expired or invalid
            if response.status_code in [401, 403]:
                logger.error(f"LinkedIn API error: {response.text}")
                return {
                    "success": False,
                    "error": "LinkedIn authentication required",
                    "needs_auth": True
                }

            if response.status_code == 201:
                logger.info("Successfully created LinkedIn post")
                return {
                    "success": True,
                    "post_id": response.headers.get("x-restli-id"),
                    "message": "Post created successfully"
                }
            else:
                error_msg = f"Failed to create post: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
            
        except Exception as e:
            error_msg = f"Error creating LinkedIn post: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def schedule_post(self, content: str, schedule_time: str, visibility: str = "PUBLIC", media_urls: list = None) -> Dict[str, Any]:
        """Schedule a post on LinkedIn."""
        try:
            # Convert schedule_time to ISO format
            schedule_datetime = datetime.fromisoformat(schedule_time)
            
            # Get user profile
            profile = await self._get_user_profile()
            
            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{profile['id']}",
                "lifecycleState": "DRAFT",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                },
                "scheduledTime": schedule_datetime.isoformat()
            }
            
            # Add media if provided
            if media_urls:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Image"
                        },
                        "media": url
                    }
                    for url in media_urls
                ]
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base_url}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                )
            
            if response.status_code != 201:
                raise Exception(f"LinkedIn API error: {response.text}")
            
            return {
                "status": "success",
                "message": "Post scheduled successfully",
                "schedule_id": response.json().get("id"),
                "scheduled_time": schedule_time
            }
            
        except Exception as e:
            logger.error(f"Error scheduling LinkedIn post: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _get_user_profile(self) -> Dict[str, Any]:
        """Get the current user's LinkedIn profile."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base_url}/me",
                    headers=self.headers
                )
            
            if response.status_code != 200:
                raise Exception(f"LinkedIn API error: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile: {str(e)}")
            raise Exception(f"Failed to get LinkedIn profile: {str(e)}")

    async def verify_token(self) -> Dict[str, Any]:
        """Verify the LinkedIn access token."""
        try:
            if not self.access_token:
                logger.error("No LinkedIn access token found")
                return {
                    "status": "error",
                    "message": "LinkedIn access token not configured. Please set LINKEDIN_ACCESS_TOKEN in .env file."
                }

            logger.info("Verifying LinkedIn token...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base_url}/me",
                    headers=self.headers
                )
            
            if response.status_code != 200:
                error_msg = f"LinkedIn API error: {response.text}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg
                }
            
            profile_data = response.json()
            logger.info(f"Successfully verified token for user: {profile_data.get('id')}")
            return {
                "status": "success",
                "message": "Token is valid",
                "profile": profile_data
            }
            
        except Exception as e:
            error_msg = f"Error verifying LinkedIn token: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }

    async def verify_token_permissions(self) -> Dict[str, Any]:
        """Verify the access token permissions."""
        try:
            self._validate_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with requests.Session() as session:
                response = session.get(
                    f"{self.api_base_url}/userinfo",
                    headers=headers
                )
                
                response.raise_for_status()
                user_info = response.json()
                
                # Log permissions
                logger.info("Token Permissions:")
                logger.info(json.dumps(user_info.get("permissions", []), indent=2))
                
                # Check for required permissions
                required_permissions = ["w_organization_social", "r_organization_social"]
                missing_permissions = [perm for perm in required_permissions 
                                    if perm not in user_info.get("permissions", [])]
                
                if missing_permissions:
                    logger.error(f"❌ Missing required permissions: {missing_permissions}")
                else:
                    logger.info("✅ All required permissions are present")
                
                return user_info
                
        except requests.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to LinkedIn API: {str(e)}")
        except requests.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
            raise Exception(f"LinkedIn API returned an error: {str(e)}")
        except Exception as e:
            logger.error(f"Error verifying token permissions: {str(e)}")
            raise Exception(f"Failed to verify token permissions: {str(e)}")
            
    async def get_organization_info(self) -> Dict[str, Any]:
        """Get information about the organization."""
        try:
            self._validate_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with requests.Session() as session:
                response = session.get(
                    f"{self.api_base_url}/organizations/{self.organization_urn}",
                    headers=headers
                )
                
                response.raise_for_status()
                org_info = response.json()
                
                # Log organization info
                logger.info("Organization Information:")
                logger.info(json.dumps(org_info, indent=2))
                
                return org_info
                
        except requests.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to LinkedIn API: {str(e)}")
        except requests.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
            raise Exception(f"LinkedIn API returned an error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting organization info: {str(e)}")
            raise Exception(f"Failed to get organization info: {str(e)}")

    async def get_profile_urn(self, access_token: str) -> Optional[str]:
        """
        Get the LinkedIn profile URN for the authenticated user.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base_url}/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                
                if response.status_code == 200:
                    profile_data = response.json()
                    return f"urn:li:person:{profile_data.get('id')}"
                else:
                    logger.error(f"Failed to get profile URN: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error getting profile URN: {str(e)}")
            return None

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate if the LinkedIn access token is still valid.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_base_url}/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False

    async def post_to_linkedin(self, content: str) -> Dict:
        """
        Post content to LinkedIn
        """
        if not self.access_token:
            return {
                "success": False,
                "error": "LinkedIn access token not configured"
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First, create a share
                response = await client.post(
                    f"{self.api_base_url}/ugcPosts",
                    headers=self.headers,
                    json={
                        "author": f"urn:li:person:{self.user_id}",
                        "lifecycleState": "PUBLISHED",
                        "specificContent": {
                            "com.linkedin.ugc.ShareContent": {
                                "shareCommentary": {
                                    "text": content
                                },
                                "shareMediaCategory": "NONE"
                            }
                        },
                        "visibility": {
                            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                        }
                    }
                )

                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "message": "Post successfully published to LinkedIn",
                        "post_id": response.headers.get("x-restli-id")
                    }
                else:
                    error_msg = f"LinkedIn API error: {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }

        except Exception as e:
            error_msg = f"Error posting to LinkedIn: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            } 