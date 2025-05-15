from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict
import httpx
import logging
import secrets
import json
from urllib.parse import urlencode
import os

from ...core.config import settings
from ...db.session import get_db
from ...db.models import User
from ...core.security import create_access_token, verify_password, get_password_hash, decode_token
from ...services.tasks import generate_linkedin_post, post_to_linkedin, schedule_linkedin_post, analyze_linkedin_engagement
from ...db import models, schemas

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

@router.get("/linkedin/verify")
async def verify_linkedin_auth():
    """
    Verify LinkedIn authentication status
    """
    try:
        linkedin_service = LinkedInService()
        is_valid = await linkedin_service.verify_authentication()
        
        return {
            "success": is_valid,
            "message": "LinkedIn authentication is valid" if is_valid else "LinkedIn authentication required"
        }
    except Exception as e:
        logger.error(f"Error verifying LinkedIn auth: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying authentication: {str(e)}"
        }

@router.get("/linkedin/login")
async def linkedin_login():
    """
    Get LinkedIn login URL
    """
    try:
        # Generate a random state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state in session or database for verification
        os.environ["LINKEDIN_OAUTH_STATE"] = state
        
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "state": state,
            "scope": "r_liteprofile r_emailaddress w_member_social"
        }
        
        # Build the authorization URL
        auth_url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"
        logger.info(f"Generated LinkedIn auth URL: {auth_url}")
        
        return {
            "url": auth_url
        }
    except Exception as e:
        logger.error(f"Error generating LinkedIn login URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn login URL: {str(e)}"
        )

@router.get("/linkedin/callback")
async def linkedin_callback(code: str = None, state: str = None):
    """
    Handle LinkedIn OAuth callback
    """
    try:
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Authorization code is required"
            )
            
        # Verify state parameter if you're using it
        stored_state = os.environ.get("LINKEDIN_OAUTH_STATE")
        if state and stored_state and state != stored_state:
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LINKEDIN_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                    "client_id": settings.LINKEDIN_CLIENT_ID,
                    "client_secret": settings.LINKEDIN_CLIENT_SECRET
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to get access token: {response.text}"
                )
            
            token_data = response.json()
            logger.info("Received token data from LinkedIn")
            
            # Store tokens in environment variables
            os.environ["LINKEDIN_ACCESS_TOKEN"] = token_data["access_token"]
            
            # Check if refresh token is present
            if "refresh_token" in token_data:
                logger.info("Refresh token received")
                os.environ["LINKEDIN_REFRESH_TOKEN"] = token_data["refresh_token"]
            else:
                logger.warning("No refresh token received from LinkedIn")
            
            # Get user profile to verify token
            profile_response = await client.get(
                "https://api.linkedin.com/v2/me",
                headers={
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
            )
            
            if profile_response.status_code != 200:
                logger.error(f"Profile fetch failed: {profile_response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user profile"
                )
            
            profile_data = profile_response.json()
            logger.info(f"Successfully authenticated user: {profile_data.get('id')}")
            
            # Store user ID
            os.environ["LINKEDIN_USER_ID"] = profile_data.get("id")
            
            # Return success response instead of redirecting
            return {
                "success": True,
                "message": "Successfully authenticated with LinkedIn",
                "user_id": profile_data.get("id"),
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token")
            }
            
    except Exception as e:
        logger.error(f"Error in LinkedIn callback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user
    """
    return current_user

@router.post("/register", response_model=schemas.User)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        profile_picture=user_in.profile_picture
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/generate-post")
async def generate_post(
    topic: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a LinkedIn post using AI"""
    task = generate_linkedin_post.delay(topic, current_user.id)
    return {"task_id": task.id, "message": "Post generation started"}

@router.post("/post-to-linkedin")
async def create_post(
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post content to LinkedIn"""
    task = post_to_linkedin.delay(content, current_user.id)
    return {"task_id": task.id, "message": "Posting to LinkedIn started"}

@router.post("/schedule-post")
async def schedule_post(
    content: str,
    schedule_time: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule a post for later"""
    task = schedule_linkedin_post.delay(content, current_user.id, schedule_time)
    return {"task_id": task.id, "message": "Post scheduled successfully"}

@router.get("/post/{post_id}/engagement")
async def get_post_engagement(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement metrics for a post"""
    task = analyze_linkedin_engagement.delay(post_id)
    return {"task_id": task.id, "message": "Engagement analysis started"}

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a task"""
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }