import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..core.config import settings

logger = logging.getLogger(__name__)

class LinkedInService:
    def __init__(self):
        self.api_url = settings.LINKEDIN_API_URL
        self.timeout = settings.TIMEOUT
        self.broker_url = settings.CELERY_BROKER_URL  # typically "redis://localhost:6379/0"

    async def create_post(
        self,
        access_token: str,
        content: str,
        visibility: str = "PUBLIC",
        media_category: Optional[str] = None,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a post on LinkedIn
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare post data
                post_data = {
                    "author": f"urn:li:person:{settings.LINKEDIN_USER_ID}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": media_category or "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": visibility
                    }
                }

                # Add media if provided
                if media_url:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image"
                            },
                            "media": media_url
                        }
                    ]

                # Make API request
                response = await client.post(
                    f"{self.api_url}/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0"
                    },
                    json=post_data
                )

                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "post_id": response.headers.get("x-restli-id")
                    }
                else:
                    logger.error(f"LinkedIn API error: {response.text}")
                    return {
                        "success": False,
                        "error": f"LinkedIn API error: {response.text}"
                    }

        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_engagement_analytics(self, days: int = 30) -> Dict:
        """
        Get engagement analytics for LinkedIn posts
        """
        try:
            # Get posts from the last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get posts from LinkedIn API
            posts = await self.get_posts(start_date, end_date)
            
            # Calculate engagement metrics
            total_likes = sum(post.get('likes', 0) for post in posts)
            total_comments = sum(post.get('comments', 0) for post in posts)
            total_shares = sum(post.get('shares', 0) for post in posts)
            total_views = sum(post.get('views', 0) for post in posts)
            
            return {
                "total_posts": len(posts),
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_views": total_views,
                "average_engagement": (total_likes + total_comments + total_shares) / len(posts) if posts else 0,
                "posts": posts
            }
        except Exception as e:
            logger.error(f"Error getting engagement analytics: {str(e)}")
            raise

    async def get_post_analytics(self, days: int = 30) -> Dict:
        """
        Get analytics for LinkedIn posts
        """
        try:
            # Get posts from the last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get posts from LinkedIn API
            posts = await self.get_posts(start_date, end_date)
            
            # Calculate post metrics
            post_types = {}
            for post in posts:
                post_type = post.get('type', 'unknown')
                post_types[post_type] = post_types.get(post_type, 0) + 1
            
            return {
                "total_posts": len(posts),
                "post_types": post_types,
                "posts": posts
            }
        except Exception as e:
            logger.error(f"Error getting post analytics: {str(e)}")
            raise

    async def get_posts(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get posts from LinkedIn API within a date range
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    },
                    params={
                        "q": "author",
                        "author": f"urn:li:person:{settings.LINKEDIN_USER_ID}",
                        "start": int(start_date.timestamp() * 1000),
                        "count": 100
                    }
                )

                if response.status_code == 200:
                    posts = response.json().get("elements", [])
                    # Filter posts by date
                    filtered_posts = [
                        post for post in posts
                        if start_date <= datetime.fromtimestamp(post.get("created", {}).get("time", 0) / 1000) <= end_date
                    ]
                    return filtered_posts
                else:
                    logger.error(f"LinkedIn API error: {response.text}")
                    return []

        except Exception as e:
            logger.error(f"Error getting LinkedIn posts: {str(e)}")
            return [] 