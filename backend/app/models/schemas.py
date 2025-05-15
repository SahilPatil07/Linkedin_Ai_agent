from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: str = datetime.now().isoformat()

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of chat messages")
    model: Optional[str] = None
    stream: bool = Field(False, description="Whether to stream the response")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Generated response text")
    posts: List[Dict[str, Any]] = Field(default_factory=list, description="List of generated posts")
    status: str = Field("success", description="Status of the response")
    conversation_history: List[Dict[str, str]] = Field(..., description="Updated conversation history")

class PostBase(BaseModel):
    content: str
    visibility: Optional[str] = "PUBLIC"
    media_category: Optional[str] = "NONE"
    media_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostRequest(PostCreate):
    chat_history: Optional[List[dict]] = None

class PostResponse(PostBase):
    id: int
    status: str
    linkedin_post_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    status: str = Field("error", description="Error status")
    message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")

class ScheduleRequest(BaseModel):
    session_id: str
    post_content: str
    schedule_time: str
    content: str = Field(..., description="Content of the post")
    visibility: str = Field("PUBLIC", description="Visibility of the post (PUBLIC/CONNECTIONS)")
    media_urls: Optional[List[str]] = Field(None, description="List of media URLs to attach")

class ScheduleResponse(BaseModel):
    status: str = Field(..., description="Status of the scheduling")
    message: str = Field(..., description="Response message")
    scheduled_post: Optional[dict] = None
    schedule_id: str = Field(..., description="ID of the scheduled post")

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 