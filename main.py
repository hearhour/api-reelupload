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
import json
import requests
import asyncio
import threading


from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from connection import Base, SessionLocal
app = FastAPI()
connected_clients = set()
__WEBSOCKETS = []
__BAKONG_URL = "https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5"
__BAKONG_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2OTg4MjI0NjAsImlhdCI6MTY5MDc4NzI2MCwiZGF0YSI6eyJpZCI6IjMyNzc5MDhjYWVhNTQzMyJ9fQ.X80yVzrIjq6L73KaDPk26WYPCCUe87YxX9GXWWixbjY'
running = False

        
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



async def get_client_ip(websocket: WebSocket = Depends()):
    return 


class Payment(Base):
    __tablename__ = "payment"
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    hash = Column(Text)
    md5 = Column(Text)
    date = Column(DateTime)
    amount = Column(Float)
    ip = Column(String(50))
    buykey = Column(Text)
    
    

    
    
    
def generate_key(amount):
    match float(amount):
        case 10.0: 
            response = requests.get("http://139.180.147.46/farmreel/buykey?token=3991&month=1")
            if response.status_code != 200: return None
            return response.json()["Buykey"]
        case 30.0: 
            response = requests.get("http://139.180.147.46/farmreel/buykey?token=3991&month=3")
            if response.status_code != 200: return None
            return response.json()["Buykey"]
        case _: return None
    


def verify_payment(md5: str, ip: str):
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + __BAKONG_TOKEN
    }

    payload = json.dumps({"md5": md5})
    response = requests.request("POST", __BAKONG_URL, headers=headers, data=payload)
    if response.status_code != 200:
        return None
    response = response.json()
   
    if "errorCode" in response:
        if response["errorCode"] in [1, 3]:
            return None
    
    hash = response["data"]["hash"]
    _db = SessionLocal()
    
    try:
        prev = _db.query(Payment).filter(Payment.hash == hash).one_or_none()
        if prev is not None:
            return None
        
        if response["data"]["toAccountId"] != "heang_lyhour@aclb":
            return None
        
        amount = response["data"]["amount"]

        buykey = generate_key(amount)
        
        if not buykey: return None
        
        _db.add(
            Payment(
                hash=hash,
                md5=md5,
                date=datetime.now(),
                amount=amount,
                ip=ip,
                buykey=buykey
            )
        )
        _db.commit()
    except:
        print("Error")
    finally:
        _db.close()
    return buykey

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

    md5 = str(md5).replace("\"", "")
    try:
        text_received = False
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=2)
                if data == "ModalClosed":
                    text_received = True
                else:
                    buykey = verify_payment(md5=md5, ip=client_host)
                    print(md5)
                    print("Buykey", buykey)
                    if buykey is not None:
                        await websocket.send_text("Buykey: {}".format(buykey))
                        await websocket.send_text("closeModal")
                        await websocket.close()
                        print('MD5 :', md5 , " Buykey : ", buykey)
                        break
                    text_received = True
            except asyncio.TimeoutError:
                if not text_received:
                    print("No text received within 5 seconds. Executing default action.")
                    buykey = verify_payment(md5=md5, ip=client_host)
                    print(md5)
                    print("Buykey", buykey)
                    if buykey is not None:
                        await websocket.send_text("Buykey: {}".format(buykey))
                        await websocket.send_text("closeModal")
                        await websocket.close()
                        break

    except WebSocketDisconnect:
        print("WebSocket Disconnected")
    finally:
        connected_clients.remove(client_host)
        
        
#I/O

app.include_router(license.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
