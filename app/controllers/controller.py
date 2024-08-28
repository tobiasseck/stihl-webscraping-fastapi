from sqlmodel import Session
from app.models.database import engine
from app.models.product import Product, Variant, Category, PriceHistory
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

class Controller:
    def __init__(self):
        self.engine = engine
        self.categories = []
        self.products = []
        self.scrape_status = "Idle"

    def get_session(self):
        return Session(self.engine)

    def scrape_all_categories(self):
        self.scrape_status = "In Progress"
        self.update_price_history()
        self.scrape_status = "Completed"

    def update_price_history(self):
        with self.get_session() as session:
            today = date.today()
            
            for product in self.products:
                db_product = session.query(Product).filter(Product.sku == product.sku).first()
                if db_product:
                    price_history = PriceHistory(
                        price_sku=product.sku,
                        price_date=today,
                        price_value=product.price,
                        product_id=db_product.id
                    )
                    session.add(price_history)
                
                for variant in product.variants:
                    db_variant = session.query(Variant).filter(Variant.sku == variant['sku']).first()
                    if db_variant:
                        price_history = PriceHistory(
                            price_sku=variant['sku'],
                            price_date=today,
                            price_value=variant['price'],
                            variant_id=db_variant.id
                        )
                        session.add(price_history)
            
            session.commit()

    def get_scrape_status(self):
        return self.scrape_status

controller = Controller()