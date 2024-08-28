from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from dotenv import load_dotenv
import os

from app.models.database import engine
from app.routers import products, scraper

load_dotenv()

app = FastAPI()

SQLModel.metadata.create_all(engine)

app.include_router(products.router)
app.include_router(scraper.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=1776)