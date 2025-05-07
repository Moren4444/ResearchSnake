import asyncio
import websockets
import json

clients = {}         # { websocket: {"id": int, "x": int, "y": int} }
next_id = 1
lock = asyncio.Lock()

async def handler(websocket):
    global next_id

    async with lock:
        client_id = next_id
        next_id += 1
        clients[websocket] = {"id": client_id, "x": 0, "y": 0, "chapter": 1, "quiz": 1}
        # Tell the client its ID
        await websocket.send(json.dumps({"type": "id", "id": client_id}))
    print(f"Client {client_id} connected.")

    try:
        async for message in websocket:
            data = json.loads(message)
            clients[websocket]["x"] = data.get("x", 0)
            clients[websocket]["y"] = data.get("y", 0)
            clients[websocket]["chapter"] = data.get("chapter", 1)
            clients[websocket]["quiz"] = data.get("quiz", 1)

            # Broadcast all client positions
            payload = [
                {"id": info["id"], "x": info["x"], "y": info["y"], "chapter": info["chapter"], "quiz": info["quiz"]}
                for info in clients.values()
            ]
            # Send to everyone
            for ws in list(clients):
                await ws.send(json.dumps({"type": "update", "clients": payload}))

    except websockets.ConnectionClosed:
        pass
    finally:
        print(f"Client {client_id} disconnected.")
        async with lock:
            if websocket in clients:
                del clients[websocket]

async def broadcast(message):
    for ws in list(clients):
        try:
            await ws.send(message)
        except Exception:
            continue

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
