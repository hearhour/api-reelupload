from typing import Union
from fastapi.staticfiles import StaticFiles
from reelupload import license
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost:3000",
#     "http://localhost:8080",
# ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# async def check_origin(request: Request):
#     if str(request.url) == "https://farmreel.mmoshop.me/farmreel/changekey":
#         return True
#     return False

# @app.middleware("http")
# async def apply_cors_to_specific_routes(request: Request, call_next):
#     if await check_origin(request):
#         response = await call_next(request)
#         response.headers["Access-Control-Allow-Origin"] = "https://farmreel.mmoshop.me"
#         response.headers["Access-Control-Allow-Methods"] = "*"
#         response.headers["Access-Control-Allow-Headers"] = "*"
#         return response
#     else:
#         raise HTTPException(
#             status_code=403,
#             detail="Forbidden",
#         )


if not os.path.exists("version"):
    os.makedirs("version")
app.mount("/version", StaticFiles(directory="version"), name="version")

app.include_router(license.router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

