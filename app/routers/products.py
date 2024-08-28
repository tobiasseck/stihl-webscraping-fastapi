from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from app.models.database import get_session
from app.models.product import Product, Category
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/products", response_model=List[Product])
async def get_products(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    query = select(Product).offset(skip).limit(limit)
    if category:
        query = query.join(Category).where(Category.name == category)
    products = session.exec(query).all()
    return products

@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    *,
    product_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_active_user)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories", response_model=List[Category])
async def get_categories(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_active_user)
):
    categories = session.exec(select(Category)).all()
    return categories