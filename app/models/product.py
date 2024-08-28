from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from datetime import date

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    link: str

    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    link: str
    description: Optional[str] = Field(default=None)
    sku: str = Field(unique=True, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="products")
    variants: List["Variant"] = Relationship(back_populates="product")
    price_histories: List["PriceHistory"] = Relationship(back_populates="product")

class Variant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: Optional[str] = Field(default=None)
    sku: str = Field(unique=True, index=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")

    product: Optional[Product] = Relationship(back_populates="variants")
    price_histories: List["PriceHistory"] = Relationship(back_populates="variant")

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    price_sku: str = Field(index=True)
    price_date: date = Field(index=True)
    price_value: float
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    variant_id: Optional[int] = Field(default=None, foreign_key="variant.id")

    product: Optional[Product] = Relationship(back_populates="price_histories")
    variant: Optional[Variant] = Relationship(back_populates="price_histories")