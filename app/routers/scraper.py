from fastapi import APIRouter, Depends, BackgroundTasks
from app.controllers.controller import controller
from app.auth import get_current_active_user
from app.views.ui import View
from app.models.user import User
from app.scraper import Scraper

router = APIRouter()

@router.post("/scrape")
async def start_scrape(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_active_user)):
    background_tasks.add_task(Scraper.start_scrape)
    return {"message": "Scraping started in the background"}

@router.get("/scrape/status")
async def get_scrape_status(current_user: User = Depends(get_current_active_user)):
    return {"status": Scraper.status}

@router.get("/export/excel")
async def export_excel(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_active_user)):
    background_tasks.add_task(View.save_to_excel, 'stihl_products_export.xlsx', controller.categories, controller.products)
    return {"message": "Excel export started in the background"}

@router.get("/export/json")
async def export_json(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_active_user)):
    background_tasks.add_task(View.save_to_json, 'stihl_products_export.json', controller.products)
    return {"message": "JSON export started in the background"}