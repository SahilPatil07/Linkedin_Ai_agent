from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    linkedin_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    content: str
    visibility: str = "PUBLIC"
    media_category: Optional[str] = "NONE"
    media_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    status: str
    linkedin_post_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LinkedInPostBase(BaseModel):
    content: str

class LinkedInPostCreate(LinkedInPostBase):
    pass

class LinkedInPost(LinkedInPostBase):
    id: int
    user_id: int
    linkedin_post_id: Optional[str]
    likes: int = 0
    comments: int = 0
    shares: int = 0
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScheduledPostBase(BaseModel):
    content: str
    scheduled_time: datetime

class ScheduledPostCreate(ScheduledPostBase):
    pass

class ScheduledPost(ScheduledPostBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostAnalyticsBase(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0

class PostAnalyticsCreate(PostAnalyticsBase):
    post_id: int

class PostAnalytics(PostAnalyticsBase):
    id: int
    post_id: int
    analytics_data: Optional[dict] = None
    updated_at: datetime

    class Config:
        from_attributes = True 