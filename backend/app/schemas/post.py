from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    content: str
    visibility: str = "PUBLIC"
    media_category: Optional[str] = None
    media_url: Optional[str] = None

class PostCreate(PostBase):
    num_posts: Optional[int] = 1

class PostCard(PostBase):
    id: Optional[int] = None
    status: str = "DRAFT"
    scheduled_time: Optional[datetime] = None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

class PostResponse(PostBase):
    id: int
    status: str
    created_at: datetime
    posted_at: Optional[datetime] = None
    scheduled_time: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True 