# app/testing/smoke_test.py
import asyncio, websockets, json

async def test():
    async with websockets.connect("ws://localhost:8000/ws/chat") as ws:
        # 1) greet arrives
        print(await ws.recv())

        s = "sess-42"
        u = "alex"

        # Turn 1
        await ws.send(json.dumps({"session_id": s, "user_id": u, "text": "I like to eat mangoes."}))
        while True:
            m = await ws.recv()
            print(m)
            if '"type":"meta"' in m:  # end of turn
                break

        # Turn 2
        await ws.send(json.dumps({"session_id": s, "user_id": u, "text": "What do I like to eat?"}))
        while True:
            m = await ws.recv()
            print(m)
            if '"type":"meta"' in m:
                break

if __name__ == "__main__":
    asyncio.run(test())
