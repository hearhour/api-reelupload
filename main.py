from typing import Union
from fastapi.staticfiles import StaticFiles
from reelupload import license
from fastapi import Depends, FastAPI
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    redis_conn = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)


if not os.path.exists("version"):
    os.makedirs("version")
app.mount("/version", StaticFiles(directory="version"), name="version")

app.include_router(license.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
