from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from ...core.config import settings
from ...db.session import get_db
from ...db import models, schemas
from ...core.security import get_current_user
from ...services.tasks import generate_linkedin_post, post_to_linkedin, schedule_linkedin_post
from ...services.linkedin_service import LinkedInService

router = APIRouter()
logger = logging.getLogger(__name__)
linkedin_service = LinkedInService()

class PostRequest(BaseModel):
    content: str = Field(..., description="The content to post on LinkedIn")
    visibility: str = Field(default="PUBLIC", description="Post visibility (PUBLIC, CONNECTIONS, etc.)")

class PostResponse(BaseModel):
    success: bool = Field(..., description="Whether the post was successful")
    message: Optional[str] = Field(None, description="Success message")
    error: Optional[str] = Field(None, description="Error message if the post failed")
    post_id: Optional[str] = Field(None, description="LinkedIn post ID if successful")

@router.post("/generate", response_model=schemas.LinkedInPost)
async def generate_post(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    topic: str
) -> Any:
    """
    Generate a LinkedIn post using AI
    """
    task = generate_linkedin_post.delay(topic, current_user.id)
    return {"task_id": task.id, "message": "Post generation started"}

@router.post("/publish", response_model=schemas.LinkedInPost)
async def publish_post(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    post_in: schemas.LinkedInPostCreate
) -> Any:
    """
    Publish a post to LinkedIn
    """
    task = post_to_linkedin.delay(post_in.content, current_user.id)
    return {"task_id": task.id, "message": "Posting to LinkedIn started"}

@router.post("/schedule", response_model=schemas.ScheduledPost)
async def schedule_post(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    post_in: schemas.ScheduledPostCreate
) -> Any:
    """
    Schedule a post for later
    """
    task = schedule_linkedin_post.delay(post_in.content, current_user.id, post_in.scheduled_time)
    return {"task_id": task.id, "message": "Post scheduled successfully"}

@router.get("/", response_model=List[schemas.LinkedInPost])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get all posts for the current user
    """
    posts = db.query(models.LinkedInPost).filter(
        models.LinkedInPost.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return posts

@router.get("/scheduled", response_model=List[schemas.ScheduledPost])
async def get_scheduled_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get all scheduled posts for the current user
    """
    posts = db.query(models.ScheduledPost).filter(
        models.ScheduledPost.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return posts

@router.post("/post-now/{post_id}", response_model=schemas.PostResponse)
async def post_now(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Post a generated card immediately to LinkedIn.
    """
    try:
        # Get the post
        post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user has LinkedIn access token
        if not current_user.linkedin_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="LinkedIn access token not found. Please authenticate with LinkedIn first."
            )
        
        # Post to LinkedIn
        linkedin_service = LinkedInService()
        success = await linkedin_service.create_post(
            access_token=current_user.linkedin_access_token,
            content=post.content,
            visibility=post.visibility
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to post to LinkedIn"
            )
        
        # Update post status
        post.status = "POSTED"
        post.posted_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
        
        return schemas.PostResponse.from_orm(post)
        
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/cancel/{post_id}", response_model=schemas.PostResponse)
async def cancel_scheduled_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a scheduled post"""
    try:
        post = db.query(models.Post).filter(
            models.Post.id == post_id,
            models.Post.user_id == current_user.id
        ).first()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        post.status = "CANCELLED"
        db.commit()
        db.refresh(post)
        
        return schemas.PostResponse.from_orm(post)
        
    except Exception as e:
        logger.error(f"Error cancelling post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/linkedin", response_model=schemas.PostResponse)
async def create_linkedin_post(
    post: schemas.PostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a post on LinkedIn.
    """
    try:
        # Validate LinkedIn access token
        if not current_user.linkedin_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="LinkedIn access token not found"
            )

        # Create post on LinkedIn
        linkedin_service = LinkedInService()
        result = await linkedin_service.create_post(
            access_token=current_user.linkedin_access_token,
            content=post.content,
            visibility=post.visibility,
            media_category=post.media_category,
            media_url=post.media_url
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # Save post to database
        db_post = models.Post(
            user_id=current_user.id,
            content=post.content,
            linkedin_post_id=result["post_id"],
            status="PUBLISHED",
            visibility=post.visibility,
            media_category=post.media_category,
            media_url=post.media_url
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        return schemas.PostResponse.from_orm(db_post)

    except Exception as e:
        logger.error(f"Error creating LinkedIn post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create LinkedIn post: {str(e)}"
        )

@router.get("/linkedin", response_model=List[schemas.PostResponse])
async def get_user_posts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all posts created by the current user.
    """
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    return [schemas.PostResponse.from_orm(post) for post in posts]

@router.post("/post", response_model=PostResponse)
async def create_post(request: PostRequest = Body(...)):
    """
    Create a post on LinkedIn
    """
    try:
        result = await linkedin_service.create_post(
            content=request.content,
            visibility=request.visibility
        )
        
        if not result["success"]:
            return PostResponse(
                success=False,
                error=result["error"]
            )
            
        return PostResponse(
            success=True,
            message=result["message"],
            post_id=result.get("post_id")
        )
        
    except Exception as e:
        return PostResponse(
            success=False,
            error=str(e)
        ) 