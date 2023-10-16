from typing import Union
from fastapi.staticfiles import StaticFiles
from reelupload import license
from fastapi import Depends, FastAPI, WebSocket, Header, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as aioredis
import time

app = FastAPI()
connected_clients = set()
__WEBSOCKETS = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if not os.path.exists("version"):
    os.makedirs("version")
app.mount("/version", StaticFiles(directory="version"), name="version")

@app.on_event("startup")
async def startup():
    redis_conn = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)



app.include_router(license.router)


async def get_client_ip(websocket: WebSocket = Depends()):
    return 

@app.websocket("/payment")
async def websocket_endpoint(websocket: WebSocket, md5: str):
    await websocket.accept()
    client_host = websocket.headers.get("X-Forwarded-For")
    if client_host:
        client_host = client_host.split(',')[0]
    else:
        client_host = websocket.client.host
    # print('real IP :', client_host)
    # print('md5 :', md5)
    # print(connected_clients)

    if client_host in connected_clients:
        await websocket.send_text("closeModal")
        await websocket.close()
        return
    else:
        connected_clients.add(client_host)

    try:
        while True:
            message = await websocket.receive_text()
            print(message)
            await websocket.send_text(message)
    except WebSocketDisconnect:
        print("WebSocket Disconnected")
    finally:
        connected_clients.remove(client_host)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
