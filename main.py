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
from contextlib import contextmanager
from connection import get_mysql_farmreel

import random

from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Date
from connection import Base, SessionLocal
app = FastAPI()
#docs_url=None, redoc_url=None,
connected_clients = set()
__WEBSOCKETS = []
__BAKONG_URL = "https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5"
__BAKONG_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MDczMjc0NzQsImlhdCI6MTY5OTI5MjI3NCwiZGF0YSI6eyJpZCI6IjMyNzc5MDhjYWVhNTQzMyJ9fQ.J0yATlhyfsfPHP_hUV8dp3zBpQwWiBXxiaXFgwYIFno'
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

async def startup():
    redis_conn = await aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)

app.add_event_handler("startup", startup)


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
    telegram = Column(Text)
    

class Telegram(Base):
    __tablename__ = "telgram"
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    link = Column(Text)
    join = Column(Text)
    

class LinkDownload(Base):
    __tablename__ = "linkdownload"
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    link = Column(Text)
    key = Column(Text)
    date = Column(Date, default=date.today())
    
    
def buykey(month: int, note: str = '', name: str = ''):
    try:
        if month == 1:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FARMREEL1' + result_str
        elif month == 3:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FARMREEL3' + result_str
        elif month == 0:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FREE' + result_str
        db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)
        insert_query = "INSERT INTO users (buykey, note, name) VALUES (%s, %s, %s)"  # Add "note" field
        cursor.execute(insert_query, (Key, note, name))  # Pass the "note" parameter
        db.commit()
        return {"Buykey": Key}
    except:
        return None
    
def generate_key(amount):
    match float(amount):
        case 10.0: 
            response = buykey(1)
            if response is None : return None
            return response["Buykey"]
        case 30.0: 
            response = buykey(3)
            if response is None : return None
            return response["Buykey"]
        case _: return None
    


ERROR_CODES = {1, 3}
ACCOUNT_ID = "heang_lyhour@aclb"


@contextmanager
def session_scope(session):
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()
        

def get_link_telegram():
    with session_scope(SessionLocal()) as _db:
        prev = _db.query(Telegram).filter(Telegram.join == 'True').first()
        if prev:
            print(prev.link)
            prev.join = 'False'
            _db.commit()
            return prev.link
        else:
            return "No Data"



def verify_payment(md5: str, ip: str):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + __BAKONG_TOKEN
    }

    payload = json.dumps({"md5": md5})
    response = requests.post(__BAKONG_URL, headers=headers, data=payload)
    if response.status_code != 200:
        return None

    response = response.json()
    if "errorCode" in response and response["errorCode"] in ERROR_CODES:
        return None

    try:
        hash = response["data"]["hash"]
        with session_scope(SessionLocal()) as _db:
            prev = _db.query(Payment).filter(Payment.hash == hash).one_or_none()
            if prev is not None:
                return None

            if response["data"]["toAccountId"] != ACCOUNT_ID:
                return None

            amount = response["data"]["amount"]
            buykey = generate_key(amount)
            telegram_join = get_link_telegram()

            if not buykey:
                return None

            _db.add(
                Payment(
                    hash=hash,
                    md5=md5,
                    date=datetime.now(),
                    amount=amount,
                    ip=ip,
                    buykey=buykey,
                    telegram=telegram_join,
                    
                )
            )
            return {'buykey' : buykey, 'telgram' : telegram_join}
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    


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
    print(md5)
    try:
        text_received = False
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=2)
                if data == "ModalClosed":
                    text_received = True
                else:
                    buykey = verify_payment(md5=md5, ip=client_host)
                    if buykey is not None:
                        await websocket.send_text("Buykey: {}".format(buykey))
                        await websocket.send_text("closeModal")
                        await websocket.close()
                        print('MD5 :', md5 , " Buykey : ", buykey)
                        break
                    text_received = True
            except asyncio.TimeoutError:
                if not text_received:
                    print("IP Connection : ", client_host)
                    buykey = verify_payment(md5=md5, ip=client_host)
                    if buykey is not None:
                        await websocket.send_text("Buykey: {}".format(buykey))
                        await websocket.send_text("closeModal")
                        await websocket.close()
                        print('MD5 :', md5 , " Buykey : ", buykey)
                        break

    except WebSocketDisconnect:
        print("WebSocket Disconnected")
    finally:
        connected_clients.remove(client_host)
        
        
#I/O


@app.get("/update_links")
def update_key(link_to_add,key):
    
    # link_to_add = 'test2'
    
    with session_scope(SessionLocal()) as _db:
        # Check if the link already exists
        existing_link = _db.query(LinkDownload).filter(LinkDownload.link == link_to_add).first()
        
        if existing_link:
            # Link already exists, you may choose to handle this situation accordingly
            raise HTTPException(status_code=400, detail="Link already exists")
        
        # If the link doesn't exist, add a new record
        _db.add(
            LinkDownload(
                link=link_to_add,
                key=key,
            )
        )
    return True

app.include_router(license.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
