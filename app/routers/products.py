from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.database import get_session
from app.models.product import Product, Category, Variant
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/products", response_model=List[dict])
async def get_products(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_active_user)
):
    products = session.exec(select(Product)).all()
    result = []
    for product in products:
        product_dict = product.dict()
        product_dict['category'] = product.category.dict() if product.category else None
        product_dict['variants'] = [
            {
                "id": variant.id,
                "name": variant.name,
                "sku": variant.sku,
                "image_url": variant.image_url,
                # Include other relevant variant fields
            }
            for variant in product.variants
        ]
        result.append(product_dict)
    return result

@router.get("/categories", response_model=List[Category])
async def get_categories(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_active_user)
):
    categories = session.exec(select(Category)).all()
    return categories