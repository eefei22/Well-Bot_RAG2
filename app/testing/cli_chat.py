import asyncio
import json
import uuid
import websockets

WS_URL = "ws://localhost:8000/ws/chat"
SESSION_ID = f"sess-{uuid.uuid4().hex[:8]}"
USER_ID = "alex"  # change if you want

async def chat():
    print(f"(connecting to {WS_URL})\nsession_id={SESSION_ID}, user_id={USER_ID}\n")
    async with websockets.connect(WS_URL) as ws:
        # optional: read initial greeting
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            print(decode_frame(msg), end="", flush=True)
        except asyncio.TimeoutError:
            pass

        while True:
            user_text = input("\nYou: ").strip()
            if not user_text:
                continue
            if user_text.lower() == "exit":
                # still send to server so it closes cleanly
                await ws.send(json.dumps({"session_id": SESSION_ID, "user_id": USER_ID, "text": "exit"}))
                print("Exiting chat.")
                break

            # send user message
            payload = {"session_id": SESSION_ID, "user_id": USER_ID, "text": user_text}
            await ws.send(json.dumps(payload))

            # stream assistant reply until we see the meta frame
            print("Well‑Bot: ", end="", flush=True)
            while True:
                raw = await ws.recv()
                obj = json.loads(raw)
                t = obj.get("type")
                if t == "token":
                    print(obj.get("text", ""), end="", flush=True)
                elif t == "meta":
                    # you can inspect retrieval/usage if you want
                    # print(f"\n[meta] {obj}")
                    print()  # newline after assistant reply
                    break
                elif t == "error":
                    print(f"\n[error] {obj.get('message')}")
                    break
                elif t == "done":
                    print()
                    break

def decode_frame(raw: str) -> str:
    try:
        obj = json.loads(raw)
        if obj.get("type") == "token":
            return obj.get("text", "")
    except Exception:
        pass
    return ""

if __name__ == "__main__":
    asyncio.run(chat())
