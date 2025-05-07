from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    timestamp: str = datetime.now().isoformat()

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    posts: Optional[List[str]] = None
    status: str = "success"
    conversation_history: List[dict]

class PostRequest(BaseModel):
    topic: str
    chat_history: Optional[List[dict]] = None

class PostResponse(BaseModel):
    posts: List[str]
    status: str = "success"
    message: str = "Posts generated successfully"

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_type: str

class ScheduleRequest(BaseModel):
    session_id: str
    post_content: str
    schedule_time: str

class ScheduleResponse(BaseModel):
    status: str
    message: str
    scheduled_post: Optional[dict] = None 