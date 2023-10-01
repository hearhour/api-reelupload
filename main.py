from typing import Union
from fastapi.staticfiles import StaticFiles
from reelupload import license
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
app = FastAPI()


if not os.path.exists("version"):
    os.makedirs("version")
app.mount("/version", StaticFiles(directory="version"), name="version")

app.include_router(license.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

