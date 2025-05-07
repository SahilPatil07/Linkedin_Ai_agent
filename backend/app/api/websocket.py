from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from app.services.llm_generator import LLMGenerator
from app.services.chat_processor import ChatProcessor
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Connect a new client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Disconnect a client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a client."""
        await websocket.send_json(message)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connections for streaming chat."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive and parse the message
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
                chat_history = message_data.get("chat_history", [])
                
                # Initialize LLM generator
                generator = LLMGenerator()
                
                # Set up accumulator for the full response
                full_response = ""
                
                # Stream the response
                async for chunk in generator.generate_posts_async(user_message, chat_history, stream=True):
                    # Send the chunk to the client
                    await manager.send_message(websocket, chunk)
                    
                    # Accumulate the full response
                    if "content" in chunk:
                        full_response += chunk["content"]
                    
                # Process the complete response
                if full_response:
                    response_message, should_post, post_content = ChatProcessor.process_response(
                        full_response, user_message
                    )
                    
                    # Send the final processed result
                    await manager.send_message(websocket, {
                        "type": "complete",
                        "should_post": should_post,
                        "post_content": post_content if should_post else None
                    })
                
            except json.JSONDecodeError:
                logger.error("Failed to parse WebSocket message")
                await manager.send_message(websocket, {"error": "Invalid message format"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await manager.send_message(websocket, {"error": str(e)})
        except:
            pass
        manager.disconnect(websocket) 