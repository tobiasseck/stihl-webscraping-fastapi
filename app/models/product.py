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
    category_id: int = Field(foreign_key="category.id")

    category: Category = Relationship(back_populates="products")
    variants: List["Variant"] = Relationship(back_populates="product")
    price_history: List["PriceHistory"] = Relationship(back_populates="product")

class Variant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: Optional[str] = Field(default=None)
    sku: str = Field(unique=True, index=True)
    product_id: int = Field(foreign_key="product.id")

    product: Product = Relationship(back_populates="variants")
    price_history: List["PriceHistory"] = Relationship(back_populates="variant")

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True)
    date: date = Field(index=True)
    price: float
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    variant_id: Optional[int] = Field(default=None, foreign_key="variant.id")

    product: Optional[Product] = Relationship(back_populates="price_history")
    variant: Optional[Variant] = Relationship(back_populates="price_history")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    disabled: bool = False