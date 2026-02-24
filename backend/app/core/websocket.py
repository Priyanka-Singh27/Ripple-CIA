import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import app.core.redis as redis_core
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # Map user_id to a list of their active WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total conns for user: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass
        logger.info(f"User {user_id} disconnected.")

    async def send_personal_message(self, user_id: str, event_type: str, data: dict[str, Any]) -> None:
        """Send a message directly to all active connections for a specific user."""
        if user_id not in self.active_connections:
            return
        
        message = {"type": event_type, "data": data}
        dead_connections = []
        
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
                
        # Clean up any connections that died during send
        for dead in dead_connections:
            self.disconnect(user_id, dead)


manager = ConnectionManager()


async def listen_to_redis() -> None:
    """
    Background task that listens to a unified Redis pub/sub channel.
    Celery workers publish events here, and this task forwards them to the active WebSockets.
    """
    redis_client = await redis_core.get_redis()
    pubsub = redis_client.pubsub()
    
    # We listen on a single global events channel. 
    # Scalability note: for horizontal scaling of FastAPI nodes, this works perfectly.
    await pubsub.subscribe("ripple:events")
    
    logger.info("Started Redis WebSocket event listener.")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    target_user_id = payload.get("user_id")
                    event_type = payload.get("event")
                    data = payload.get("data", {})
                    
                    if target_user_id and event_type:
                        await manager.send_personal_message(target_user_id, event_type, data)
                except Exception as e:
                    logger.error(f"Error processing Redis WS message: {e}")
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe("ripple:events")
