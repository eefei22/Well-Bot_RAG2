import websockets, asyncio

async def test():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as ws:
        await ws.send("Hello Well-Bot")
        while True:
            msg = await ws.recv()
            print("Received:", msg)
            if msg == "[DONE]":
                break

asyncio.run(test())
