from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import csv
import json
from tqdm import tqdm
from sqlmodel import Session
from app.models.database import engine
from app.models.product import Category, Product, Variant, PriceHistory
from datetime import date

class Scraper:
    def __init__(self):
        self.progress = 0
        self.status = "Idle"
        self.total_categories = 0
        self.total_products = 0
        self.driver = None
        self.base_url = "https://www.stihl.de"
        self.categories = []
        self.products = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--lang=de")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--search-engine-choice-country")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")

        service = Service('E:\Python\API\web-scraping\chromedriver-win64\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def extract_categories(self):
        categories = {}
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/de/c/"]')
            for link in links:
                href = link.get_attribute('href')
                name = link.text.strip()
                if name and href and '/de/c/' in href:
                    categories[name] = href
                    print(f"Found category: {name} - {href}")
        except Exception as e:
            print(f"Error extracting categories: {e}")
        return categories

    def get_category_count(self):
        try:
            count_element = self.driver.find_element(By.CSS_SELECTOR, ".btn_show-count")
            count_text = count_element.text
            match = re.search(r'(\d+) VON (\d+)', count_text)
            if match:
                current, total = map(int, match.groups())
                return current, total
        except Exception as e:
            print(f"Error getting category count: {e}")
        return None, None

    def load_all_categories(self):
        while True:
            current, total = self.get_category_count()
            if current is None or total is None:
                print("Could not determine category count")
                break
            
            print(f"Current categories: {current}/{total}")
            
            if current == total:
                print("All categories loaded")
                break

            try:
                show_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_show-more"))
                )
                self.driver.execute_script("arguments[0].click();", show_more_button)
                print("Clicked 'Show more' button")
                time.sleep(2)
            except TimeoutException:
                print("No more 'Show more' button found or timed out waiting for it")
                break
            except Exception as e:
                print(f"Error clicking 'Show more' button: {e}")
                break

    def scrape_categories(self):
        self.status = "Scraping categories"
        self.setup_driver()
        self.driver.get('https://www.stihl.de/de/geraete-werkzeuge')
        time.sleep(5)
        
        self.load_all_categories()
        categories_dict = self.extract_categories()
        
        self.total_categories = len(categories_dict)
        self.progress = 50  # Categories are 50% of total progress

        with Session(engine) as session:
            for name, link in categories_dict.items():
                category = Category(name=name, link=link)
                session.add(category)
                self.categories.append({'name': name, 'link': link})
            session.commit()

        self.driver.quit()

    def scrape_product_details(self, product):
        response = requests.get(product.link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        script = soup.find('script', type='application/ld+json')
        if script:
            data = json.loads(script.string)
            
            product.description = data.get('description', '')

            if 'model' in data:
                for variant_data in data['model']:
                    variant_name = variant_data.get('name', '')
                    variant_price = variant_data.get('offers', {}).get('price', 'N/A')
                    variant_sku = variant_data.get('sku', '')
                    self.add_variant(product, variant_name, variant_price, variant_sku)

            if product.variants:
                product.sku = product.variants[0].sku

        return product

    def scrape_products(self, url, category_name):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        product_tiles = soup.find_all('a', class_='m_category-overview-tiles__item')

        category_products = []
        progress_bar = tqdm(total=len(product_tiles), desc=f"Scraping {category_name}", unit="product")

        for tile in product_tiles:
            name_element = tile.find('span', class_='tile_product-standard__title-inner')
            if name_element:
                name = name_element.text.strip()
            else:
                progress_bar.update(1)
                continue

            link = self.base_url + tile['href']
            
            price_element = tile.find('span', class_='price-value')
            price = price_element.text.strip() if price_element else "N/A"

            product = Product(name=name, link=link, description="", sku="", price=price, variants=[])
            product = self.scrape_product_details(product)
            
            self.products.append(product)
            category_products.append(product)

            time.sleep(1)
            progress_bar.update(1)

        progress_bar.close()
        return category_products

    def scrape_product_details(self, product):
        response = requests.get(product.link, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        script = soup.find('script', type='application/ld+json')
        if script:
            data = json.loads(script.string)
            
            product.description = data.get('description', '')

            if 'model' in data:
                for variant_data in data['model']:
                    variant_name = variant_data.get('name', '')
                    variant_price = variant_data.get('offers', {}).get('price', 'N/A')
                    variant_sku = variant_data.get('sku', '')
                    self.add_variant(product, variant_name, variant_price, variant_sku)

            if product.variants:
                product.sku = product.variants[0].sku

        return product

    def add_variant(self, product, variant_name, variant_price, variant_sku):
        variant_parts = variant_name.split(', ', 1)
        variant_name = variant_parts[0]
        variant_identifier = variant_parts[1] if len(variant_parts) > 1 else ""
        
        variant = Variant(
            name=variant_name,
            identifier=variant_identifier,
            sku=variant_sku,
        )
        
        if variant_price != 'N/A':
            try:
                price_value = float(variant_price.replace('€', '').replace(',', '.').strip())
            except ValueError:
                price_value = None
        else:
            price_value = None

        price_history = PriceHistory(
            price_sku=variant_sku,
            price_date=date.today(),
            price_value=price_value,
        )
        
        variant.price_histories = [price_history]
        product.variants.append(variant)


    def scrape_all_products(self):
        self.status = "Scraping products"
        self.total_products = len(self.categories)
        for i, category in enumerate(tqdm(self.categories, desc="Scraping categories", unit="category")):
            print(f"\nScraping category: {category['name']}")
            category['products'] = self.scrape_products(category['link'], category['name'])
            time.sleep(2)
            self.progress = 50 + ((i + 1) / self.total_products * 50)  # Products are the other 50%

    def save_to_db(self):
        with Session(engine) as session:
            for category in self.categories:
                db_category = session.query(Category).filter(Category.link == category['link']).first()
                if not db_category:
                    db_category = Category(name=category['name'], link=category['link'])
                    session.add(db_category)
                    session.flush()

                for product in category['products']:
                    db_product = session.query(Product).filter(Product.sku == product.sku).first()
                    if not db_product:
                        db_product = Product(
                            name=product.name,
                            link=product.link,
                            description=product.description,
                            sku=product.sku,
                            price=product.price,
                            category_id=db_category.id
                        )
                        session.add(db_product)
                        session.flush()
                    else:
                        db_product.name = product.name
                        db_product.link = product.link
                        db_product.description = product.description
                        db_product.price = product.price

                    for variant in product.variants:
                        db_variant = session.query(Variant).filter(Variant.sku == variant.sku).first()
                        if not db_variant:
                            db_variant = Variant(
                                name=variant.name,
                                identifier=variant.identifier,
                                sku=variant.sku,
                                product_id=db_product.id
                            )
                            session.add(db_variant)
                            session.flush()
                        else:
                            db_variant.name = variant.name
                            db_variant.identifier = variant.identifier

                        for price_history in variant.price_histories:
                            db_price_history = PriceHistory(
                                price_sku=price_history.price_sku,
                                price_date=price_history.price_date,
                                price_value=price_history.price_value,
                                variant_id=db_variant.id
                            )
                            session.add(db_price_history)

            session.commit()

    async def start_scrape(self):
        self.progress = 0
        self.status = "Starting"
        self.scrape_categories()
        self.scrape_all_products()
        self.save_to_db()
        self.status = "Completed"
        self.progress = 100

scraper = Scraper()