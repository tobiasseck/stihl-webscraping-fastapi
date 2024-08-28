from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from datetime import date
from sqlalchemy import Column, String, Text

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    link: str = Field(max_length=512)

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    link: str = Field(max_length=512)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    sku: str = Field(max_length=100, unique=True, index=True)
    price: Optional[str] = Field(max_length=50, default=None)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="products")
    variants: List["Variant"] = Relationship(back_populates="product")
    price_histories: List["PriceHistory"] = Relationship(back_populates="product")

class Variant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    identifier: Optional[str] = Field(default=None, max_length=512)
    sku: str = Field(max_length=100, unique=True, index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")

    product: Optional[Product] = Relationship(back_populates="variants")
    price_histories: List["PriceHistory"] = Relationship(back_populates="variant")

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    price_sku: str = Field(max_length=100, index=True)
    price_date: date = Field(index=True)
    price_value: float
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    variant_id: Optional[int] = Field(default=None, foreign_key="variant.id")

    product: Optional[Product] = Relationship(back_populates="price_histories")
    variant: Optional[Variant] = Relationship(back_populates="price_histories")