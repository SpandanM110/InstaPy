# app/__init__.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.main import router as main_router
from app.database import init_db
import asyncio

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main_router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    pass  # Add any shutdown logic if necessary
