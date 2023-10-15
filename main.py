from typing import Union
from fastapi.staticfiles import StaticFiles
from reelupload import license
from fastapi import Depends, FastAPI, WebSocket, Header
from pydantic import BaseModel
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as aioredis

app = FastAPI()

__WEBSOCKETS = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)

@app.on_event("startup")
async def startup():
 
    await FastAPILimiter.init(redis_conn)
    print(redis_conn)


if not os.path.exists("version"):
    os.makedirs("version")
app.mount("/version", StaticFiles(directory="version"), name="version")

app.include_router(license.router)


async def get_client_ip(websocket: WebSocket = Depends()):
    return 

@app.websocket("/payment")
async def websocket_endpoint(websocket: WebSocket, md5: str):
    await websocket.accept()
    # client_ip = websocket.client.host
    # await redis_conn.set(f"client_ip:{client_ip}", client_ip, expire=3600)
    # print(client_ip)

@app.get('/')
def index(real_ip: str = Header(None, alias='X-Real-IP')):
    return real_ip

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
