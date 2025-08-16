import asyncio
import json
import uuid
import websockets

WS_URL = "ws://localhost:8000/ws/chat"
SESSION_ID = f"sess-{uuid.uuid4().hex[:8]}"
USER_ID = "alex"

OPEN_TIMEOUT = 30
PING_INTERVAL = 30
PING_TIMEOUT = 30
CLOSE_TIMEOUT = 10

async def chat():
    print(f"(connecting to {WS_URL})\nsession_id={SESSION_ID}, user_id={USER_ID}\n")
    try:
        async with websockets.connect(
            WS_URL,
            open_timeout=OPEN_TIMEOUT,
            close_timeout=CLOSE_TIMEOUT,
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
        ) as ws:
            # optional greeting frame
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                print(decode_frame(msg), end="", flush=True)
            except asyncio.TimeoutError:
                pass

            while True:
                # non-blocking console input (keeps pings flowing)
                try:
                    user_text = (await asyncio.to_thread(input, "\nYou: ")).strip()
                except (EOFError, KeyboardInterrupt):
                    user_text = "exit"

                if not user_text:
                    continue

                if user_text.lower() == "exit":
                    try:
                        await ws.send(json.dumps({"session_id": SESSION_ID, "user_id": USER_ID, "text": "exit"}))
                    except Exception:
                        pass
                    print("Exiting chat.")
                    return

                payload = {"session_id": SESSION_ID, "user_id": USER_ID, "text": user_text}
                await ws.send(json.dumps(payload))

                print("\nWell-Bot: ", end="", flush=True)
                while True:
                    try:
                        raw = await ws.recv()
                    except websockets.exceptions.ConnectionClosedOK:
                        print("\n[client] server closed the connection (OK).")
                        return
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"\n[client] connection closed with error: {e}")
                        return

                    obj = json.loads(raw)
                    t = obj.get("type")
                    if t == "token":
                        print(obj.get("text", ""), end="", flush=True)
                    elif t == "meta":
                        print()
                        break
                    elif t == "error":
                        print(f"\n[error] {obj.get('message')}")
                        break
                    elif t == "done":
                        print()
                        break
    except TimeoutError as e:
        print(f"[client] handshake timed out: {e}")
    except OSError as e:
        print(f"[client] cannot connect: {e}")

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
