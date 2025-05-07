import httpx
import logging
import json
import re
from typing import Dict, Any, Optional
from app.core.config import config

logger = logging.getLogger(__name__)

class LinkedInService:
    """Service for interacting with LinkedIn API."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize with optional access token override."""
        self.access_token = access_token or config.LINKEDIN_ACCESS_TOKEN
        self.organization_urn = config.LINKEDIN_ORGANIZATION_URN
        self.api_base = "https://api.linkedin.com/rest"
        
    def _validate_access_token(self):
        """Validate that the access token is set."""
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN is not configured")
            
    def _validate_organization_urn(self, urn: str) -> bool:
        """Validate the organization URN format."""
        if not re.match(r'^urn:li:organization:\d+$', urn):
            logger.error(f"Invalid organization URN format: {urn}")
            return False
        return True
            
    async def create_post(self, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a LinkedIn post for the organization."""
        try:
            self._validate_access_token()
            
            # Validate organization URN
            if not self._validate_organization_urn(self.organization_urn):
                raise ValueError(f"Invalid organization URN format: {self.organization_urn}")
            
            # Construct the post data with the exact format from LinkedIn's example
            post_data = {
                "author": self.organization_urn,
                "commentary": content if not title else f"{title}\n\n{content}",
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                },
                "lifecycleState": "PUBLISHED"
            }
            
            # Set up headers with X-Restli-Protocol-Version instead of LinkedIn-Version
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Log the request details
            logger.info("Making LinkedIn API request:")
            logger.info(f"URL: {self.api_base}/posts")
            logger.info("Headers:")
            logger.info(json.dumps(headers, indent=2))
            logger.info("Request Body:")
            logger.info(json.dumps(post_data, indent=2))
            
            # Validate the author field in the request
            if not self._validate_organization_urn(post_data["author"]):
                raise ValueError(f"Invalid author URN in request: {post_data['author']}")
            
            async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
                response = await client.post(
                    f"{self.api_base}/posts",
                    headers=headers,
                    json=post_data
                )
                
                # Log the response details
                logger.info(f"Response Status Code: {response.status_code}")
                try:
                    response_json = response.json()
                    logger.info("Response Body:")
                    logger.info(json.dumps(response_json, indent=2))
                except json.JSONDecodeError:
                    logger.info(f"Raw Response Content: {response.content}")
                
                # Check for specific status codes
                if response.status_code in [201, 202]:
                    logger.info("✅ Post successfully created or scheduled")
                elif response.status_code == 400:
                    logger.error("❌ Bad Request - Check request format and permissions")
                elif response.status_code == 403:
                    logger.error("❌ Forbidden - Check access token and permissions")
                else:
                    logger.error(f"❌ Unexpected status code: {response.status_code}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to LinkedIn API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
            raise Exception(f"LinkedIn API returned an error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {str(e)}")
            raise Exception(f"Failed to create LinkedIn post: {str(e)}")
            
    async def verify_token_permissions(self) -> Dict[str, Any]:
        """Verify the access token permissions."""
        try:
            self._validate_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
                response = await client.get(
                    f"{self.api_base}/userinfo",
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
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to LinkedIn API: {str(e)}")
        except httpx.HTTPStatusError as e:
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
            
            async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
                response = await client.get(
                    f"{self.api_base}/organizations/{self.organization_urn}",
                    headers=headers
                )
                
                response.raise_for_status()
                org_info = response.json()
                
                # Log organization info
                logger.info("Organization Information:")
                logger.info(json.dumps(org_info, indent=2))
                
                return org_info
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Failed to connect to LinkedIn API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
            raise Exception(f"LinkedIn API returned an error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting organization info: {str(e)}")
            raise Exception(f"Failed to get organization info: {str(e)}") 