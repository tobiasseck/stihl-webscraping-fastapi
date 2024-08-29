from fastapi import APIRouter, Depends, BackgroundTasks
from app.scraper import scraper
from app.auth import get_current_active_user

router = APIRouter()

@router.post("/scrape")
async def start_scrape(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_active_user)):
    background_tasks.add_task(scraper.start_scrape)
    return {"message": "Scraping started in the background"}

@router.get("/scrape/status")
async def get_scrape_status(current_user: dict = Depends(get_current_active_user)):
    return {
        "status": scraper.status,
        "progress": scraper.progress,
        "message": f"Scrape status: {scraper.status}, Progress: {scraper.progress}%"
    }