from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta

from app.core.config import settings
from app.services.linkedin import LinkedInService

router = APIRouter()

@router.get("/engagement")
async def get_engagement_analytics(
    days: int = 30,
    linkedin_service: LinkedInService = Depends()
) -> Dict:
    """
    Get engagement analytics for LinkedIn posts
    """
    try:
        analytics = await linkedin_service.get_engagement_analytics(days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_post_analytics(
    days: int = 30,
    linkedin_service: LinkedInService = Depends()
) -> Dict:
    """
    Get analytics for LinkedIn posts
    """
    try:
        analytics = await linkedin_service.get_post_analytics(days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 