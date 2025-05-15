from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chat model")
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="Previous chat messages for context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "chat_history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello! How can I help you?"}
                ]
            }
        }

class ChatResponse(BaseModel):
    status: str = Field(..., description="Status of the response (success/error)")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if the request failed")
    is_post: bool = Field(default=False, description="Whether the response is a post") 