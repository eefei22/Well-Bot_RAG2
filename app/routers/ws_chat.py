from fastapi import APIRouter, WebSocket
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")

            # Simulate streaming by sending chunks
            for chunk in ["Echo: ", data]:
                await websocket.send_text(chunk)
            await websocket.send_text("[DONE]")
    except Exception as e:
        logger.error(f"WebSocket closed: {e}")
    finally:
        await websocket.close()
