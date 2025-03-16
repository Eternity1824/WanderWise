import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from fastapi import FastAPI
from app.routers.router import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}