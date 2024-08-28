import os
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlmodel import SQLModel, Session
from dotenv import load_dotenv
import socket
import json

from app.models.database import engine, get_session
from app.models.product import Category, Product, Variant, PriceHistory
from app.models.user import User
from app.routers import products, scraper
from app.scraper import scraper as scraper_instance
from app.auth import Token, authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

app.include_router(products.router)
app.include_router(scraper.router)

load_dotenv()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

static_dir = os.path.join(project_root, "app", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=static_dir)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "progress": scraper_instance.progress,
            "status": scraper_instance.status
        }
        await websocket.send_text(json.dumps(data))
        if scraper_instance.status == "Completed":
            break
        await asyncio.sleep(1)

@app.get("/browse", response_class=HTMLResponse)
async def browse_data(request: Request):
    return templates.TemplateResponse("browse.html", {"request": request})

@app.post("/start-scrape")
async def start_scrape():
    asyncio.create_task(scraper_instance.start_scrape())
    return {"message": "Scraping started"}

def find_free_port(start_port=8000, max_port=9000):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise OSError("No free ports found in range")

if __name__ == "__main__":
    import uvicorn
    free_port = find_free_port()
    print(f"Starting server on port {free_port}")
    uvicorn.run("app.main:app", host="127.0.0.1", port=free_port, reload=True)