import psycopg2
from psycopg2.extras import execute_values
from loguru import logger
import pandas as pd
from typing import List, Dict, Any
from . import config
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**config.DB_CONFIG)
            self.cursor = self.conn.cursor()
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
            
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    sku VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    description TEXT,
                    price DECIMAL(10, 2),
                    availability VARCHAR(50),
                    original_price DECIMAL(10, 2),
                    discount DECIMAL(5, 2),
                    range VARCHAR(255),
                    reading VARCHAR(255),
                    family VARCHAR(255),
                    weight VARCHAR(50),
                    dimensions VARCHAR(255),
                    image_url TEXT,
                    product_url TEXT,
                    category VARCHAR(255),
                    subcategory VARCHAR(255),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_logs (
                    id SERIAL PRIMARY KEY,
                    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    products_updated INTEGER,
                    products_added INTEGER,
                    status VARCHAR(50),
                    error_message TEXT
                )
            """)
            
            self.conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create tables: {str(e)}")
            raise
            
    def upsert_products(self, products: List[Dict[str, Any]]):
        """Insert or update products in bulk"""
        try:
            query = """
                INSERT INTO products (
                    sku, title, description, price, availability, original_price, 
                    discount, range, reading, family, weight, dimensions, 
                    image_url, product_url, category, subcategory
                )
                VALUES %s
                ON CONFLICT (sku) DO UPDATE
                SET title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    availability = EXCLUDED.availability,
                    original_price = EXCLUDED.original_price,
                    discount = EXCLUDED.discount,
                    range = EXCLUDED.range,
                    reading = EXCLUDED.reading,
                    family = EXCLUDED.family,
                    weight = EXCLUDED.weight,
                    dimensions = EXCLUDED.dimensions,
                    image_url = EXCLUDED.image_url,
                    product_url = EXCLUDED.product_url,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    last_updated = CURRENT_TIMESTAMP
            """
            
            values = [(
                p['sku'],
                p.get('title', ''),
                p.get('description', ''),
                p['price'],
                p['availability'],
                p['original_price'],
                p['discount'],
                p.get('range', ''),
                p.get('reading', ''),
                p.get('family', ''),
                p.get('weight', ''),
                p.get('dimensions', ''),
                p.get('image_url', ''),
                p.get('product_url', ''),
                p.get('category', ''),
                p.get('subcategory', '')
            ) for p in products]
            
            execute_values(self.cursor, query, values)
            self.conn.commit()
            logger.info(f"Successfully upserted {len(products)} products")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to upsert products: {str(e)}")
            raise
            
    def log_sync(self, products_updated: int, products_added: int, status: str, error_message: str = None):
        """Log synchronization results"""
        try:
            self.cursor.execute("""
                INSERT INTO sync_logs (products_updated, products_added, status, error_message)
                VALUES (%s, %s, %s, %s)
            """, (products_updated, products_added, status, error_message))
            
            self.conn.commit()
            logger.info("Sync log recorded successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to log sync: {str(e)}")
            raise
            
    def get_all_products(self):
        """Get all products from database with quality filters"""
        query = """
        SELECT *
        FROM products
        WHERE 1=1
        AND sku IS NOT NULL AND sku != ''  -- SKU'su olan ürünler
        AND title IS NOT NULL  -- Başlığı olan ürünler
        AND price IS NOT NULL  -- Fiyatı olan ürünler
        AND availability IS NOT NULL  -- Stok durumu belli olan ürünler
        """
        logger.info("Fetching filtered products from database...")
        return pd.read_sql_query(query, self.conn)

    def get_modified_products(self, last_sync: datetime):
        """Get products modified since last sync with quality filters"""
        query = """
        SELECT *
        FROM products
        WHERE 1=1
        AND modified_at > ?
        AND sku IS NOT NULL AND sku != ''  -- SKU'su olan ürünler
        AND title IS NOT NULL  -- Başlığı olan ürünler
        AND price IS NOT NULL  -- Fiyatı olan ürünler
        AND availability IS NOT NULL  -- Stok durumu belli olan ürünler
        """
        logger.info(f"Fetching filtered products modified since {last_sync}")
        return pd.read_sql_query(query, self.conn, params=[last_sync]) 