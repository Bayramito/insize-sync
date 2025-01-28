import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Insize credentials
INSIZE_USERNAME = os.getenv('INSIZE_USERNAME')
INSIZE_PASSWORD = os.getenv('INSIZE_PASSWORD')
INSIZE_EXCEL_URL = os.getenv('INSIZE_EXCEL_URL')

# Shopify credentials
SHOPIFY_SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Sync schedule
SYNC_TIMES = [
    os.getenv('SYNC_TIME_1'),
    os.getenv('SYNC_TIME_2')
]

# Logging configuration
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
LOG_FILE = "logs/insize_sync.log" 